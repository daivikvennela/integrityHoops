(function() {
  'use strict';

  function rafThrottle(fn) {
    let ticking = false;
    return function(...args) {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          fn.apply(this, args);
          ticking = false;
        });
        ticking = true;
      }
    };
  }

  function applyZoom(chart, start, end, neonInside) {
    const dataZoom = [ { start, end } ];
    if (neonInside) {
      dataZoom.push({ type: 'inside', zoomOnMouseWheel: true, moveOnMouseMove: true });
    }
    chart.setOption({ dataZoom }, { notMerge: false, lazyUpdate: true });
  }

  function create(opts) {
    const {
      chart,
      container,
      initialPrecision = 40,
      anchor = 'end',
      minWindow = 8
    } = opts || {};
    if (!chart || !container) return null;

    // Build DOM
    const wrapper = document.createElement('div');
    wrapper.className = 'viz-slider';

    const label = document.createElement('div');
    label.className = 'viz-slider-label';
    label.innerHTML = '<span>Precision</span><span id="vizSliderValue">' + initialPrecision + '%</span>';

    const input = document.createElement('input');
    input.className = 'viz-slider-track';
    input.type = 'range';
    input.min = '0';
    input.max = '100';
    input.value = String(initialPrecision);
    input.setAttribute('aria-label', 'Visualization precision');

    wrapper.appendChild(label);
    wrapper.appendChild(input);
    container.innerHTML = '';
    container.appendChild(wrapper);

    let neonMode = false;

    function recomputeAndApply(val) {
      const precision = Math.max(0, Math.min(100, parseInt(val, 10) || 0));
      const windowSize = Math.max(minWindow, 100 - precision);
      let start = 0, end = 100;
      if (anchor === 'end') {
        end = 100;
        start = 100 - windowSize;
      } else {
        start = 0;
        end = windowSize;
      }
      const valueEl = wrapper.querySelector('#vizSliderValue');
      if (valueEl) valueEl.textContent = precision + '%';
      try {
        applyZoom(chart, start, end, neonMode);
      } catch (e) {
        // no-op
      }
      try {
        localStorage.setItem('analyticsPrecision', String(precision));
      } catch (e) {}
    }

    const onInput = rafThrottle((e) => {
      recomputeAndApply(e.target.value);
    });

    input.addEventListener('input', onInput);
    input.addEventListener('change', (e) => recomputeAndApply(e.target.value));

    // Keyboard support is native to range inputs

    // Double click toggles neon mode and inside zoom
    input.addEventListener('dblclick', () => {
      neonMode = !neonMode;
      wrapper.classList.toggle('neon-active', neonMode);
      recomputeAndApply(input.value);
    });

    // Initialize
    recomputeAndApply(initialPrecision);

    return {
      setPrecision(p) { input.value = String(p); recomputeAndApply(p); },
      toggleNeon() { neonMode = !neonMode; wrapper.classList.toggle('neon-active', neonMode); recomputeAndApply(input.value); },
      isNeon() { return neonMode; }
    };
  }

  // Chart.js compatible slider
  function createForChartJS(opts) {
    const {
      chart,
      container,
      initialPrecision = 40,
      anchor = 'end',
      minWindow = 8
    } = opts || {};
    
    console.log('createForChartJS called with:', { chart: !!chart, container: !!container, initialPrecision });
    
    if (!chart || !container) {
      console.warn('createForChartJS: Missing chart or container', { chart: !!chart, container: !!container });
      return null;
    }

    // Store original data
    const originalData = {
      labels: [...chart.data.labels],
      datasets: chart.data.datasets.map(ds => ({
        ...ds,
        data: [...ds.data]
      }))
    };

    // Build DOM
    const wrapper = document.createElement('div');
    wrapper.className = 'viz-slider';

    const label = document.createElement('div');
    label.className = 'viz-slider-label';
    const sliderValueId = 'teamStatsSliderValue';
    label.innerHTML = '<span>Precision</span><span id="' + sliderValueId + '">' + initialPrecision + '%</span>';

    const input = document.createElement('input');
    input.className = 'viz-slider-track';
    input.type = 'range';
    input.min = '0';
    input.max = '100';
    input.value = String(initialPrecision);
    input.setAttribute('aria-label', 'Visualization precision');

    wrapper.appendChild(label);
    wrapper.appendChild(input);
    container.innerHTML = '';
    container.appendChild(wrapper);

    function recomputeAndApply(val) {
      const precision = Math.max(0, Math.min(100, parseInt(val, 10) || 0));
      const windowSize = Math.max(minWindow, 100 - precision);
      let start = 0, end = 100;
      if (anchor === 'end') {
        end = 100;
        start = 100 - windowSize;
      } else {
        start = 0;
        end = windowSize;
      }

      const valueEl = wrapper.querySelector('#' + sliderValueId);
      if (valueEl) valueEl.textContent = precision + '%';

      // Calculate visible range
      const totalLabels = originalData.labels.length;
      const startIndex = Math.floor((start / 100) * totalLabels);
      const endIndex = Math.ceil((end / 100) * totalLabels);

      // Filter labels and datasets
      const visibleLabels = originalData.labels.slice(startIndex, endIndex);
      const visibleDatasets = originalData.datasets.map(ds => ({
        ...ds,
        data: ds.data.slice(startIndex, endIndex)
      }));

      // Update chart
      try {
        chart.data.labels = visibleLabels;
        chart.data.datasets = visibleDatasets;
        chart.update('none');
      } catch (e) {
        console.error('Error updating chart:', e);
      }

      try {
        localStorage.setItem('teamStatsPrecision', String(precision));
      } catch (e) {}
    }

    const onInput = rafThrottle((e) => {
      recomputeAndApply(e.target.value);
    });

    input.addEventListener('input', onInput);
    input.addEventListener('change', (e) => recomputeAndApply(e.target.value));

    // Initialize
    recomputeAndApply(initialPrecision);

    return {
      setPrecision(p) { input.value = String(p); recomputeAndApply(p); },
      updateOriginalData() {
        // Update stored original data (call this when chart data changes)
        originalData.labels = [...chart.data.labels];
        originalData.datasets = chart.data.datasets.map(ds => ({
          ...ds,
          data: [...ds.data]
        }));
        // Reapply current precision
        recomputeAndApply(input.value);
      }
    };
  }

  window.IntegrityHoopsSlider = { create, createForChartJS };
})();


