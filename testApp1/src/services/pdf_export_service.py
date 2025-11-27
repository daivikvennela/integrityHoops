"""
PDF Export Service
Generates 2K/Madden style player performance cards as PDF files.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from datetime import datetime
import io
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PDFExportService:
    """
    Service for generating PDF player performance cards.
    """
    
    # Heat color scheme
    HEAT_RED = HexColor('#F9423A')
    HEAT_BLACK = HexColor('#000000')
    HEAT_WHITE = HexColor('#FFFFFF')
    HEAT_GRAY = HexColor('#333333')
    
    def __init__(self):
        self.page_width, self.page_height = letter
    
    def generate_player_card(self, player_data: Dict[str, Any], output_path: Optional[str] = None) -> bytes:
        """
        Generate a player performance card PDF.
        
        Args:
            player_data: Dict containing:
                - player_name: str
                - game_date: str
                - opponent: str
                - cog_score: float (overall score)
                - category_scores: dict of category: score
                - stats: dict of stat_name: value
            output_path: Optional file path to save PDF
            
        Returns:
            bytes: PDF file content
        """
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        
        # Background
        c.setFillColor(self.HEAT_BLACK)
        c.rect(0, 0, self.page_width, self.page_height, fill=1)
        
        # Top accent bar
        c.setFillColor(self.HEAT_RED)
        c.rect(0, self.page_height - 80, self.page_width, 80, fill=1)
        
        # Player name
        c.setFillColor(self.HEAT_WHITE)
        c.setFont("Helvetica-Bold", 36)
        player_name = player_data.get('player_name', 'UNKNOWN')
        c.drawCentredString(self.page_width / 2, self.page_height - 50, player_name.upper())
        
        # Game info
        c.setFont("Helvetica", 14)
        game_info = f"{player_data.get('game_date', 'N/A')} vs {player_data.get('opponent', 'N/A')}"
        c.drawCentredString(self.page_width / 2, self.page_height - 70, game_info)
        
        # Overall Cog Score (large, centered)
        cog_score = player_data.get('cog_score', 0.0)
        c.setFont("Helvetica-Bold", 72)
        c.setFillColor(self.HEAT_RED)
        c.drawCentredString(self.page_width / 2, self.page_height - 200, f"{cog_score:.1f}")
        
        c.setFont("Helvetica", 16)
        c.setFillColor(self.HEAT_WHITE)
        c.drawCentredString(self.page_width / 2, self.page_height - 225, "COGNITIVE SCORE")
        
        # Category breakdown
        y_position = self.page_height - 300
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(self.HEAT_RED)
        c.drawString(50, y_position, "CATEGORY BREAKDOWN")
        
        y_position -= 30
        category_scores = player_data.get('category_scores', {})
        
        for category, score in sorted(category_scores.items(), key=lambda x: x[1], reverse=True):
            c.setFont("Helvetica", 12)
            c.setFillColor(self.HEAT_WHITE)
            c.drawString(60, y_position, category)
            
            # Progress bar
            bar_x = 250
            bar_width = 250
            bar_height = 15
            
            # Background bar
            c.setFillColor(self.HEAT_GRAY)
            c.rect(bar_x, y_position - 3, bar_width, bar_height, fill=1)
            
            # Filled bar
            fill_width = (score / 100) * bar_width
            c.setFillColor(self.HEAT_RED)
            c.rect(bar_x, y_position - 3, fill_width, bar_height, fill=1)
            
            # Score text
            c.setFillColor(self.HEAT_WHITE)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(bar_x + bar_width + 10, y_position, f"{score:.1f}")
            
            y_position -= 25
            
            if y_position < 100:
                break
        
        # Footer
        c.setFont("Helvetica", 10)
        c.setFillColor(self.HEAT_GRAY)
        c.drawCentredString(
            self.page_width / 2, 
            30, 
            f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | IntegrityHoops Analytics"
        )
        
        c.showPage()
        c.save()
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        # Save to file if path provided
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)
            logger.info(f"Player card saved to {output_path}")
        
        return pdf_bytes
    
    def generate_comparison_card(self, players_data: list, output_path: Optional[str] = None) -> bytes:
        """
        Generate a comparison card for multiple players.
        
        Args:
            players_data: List of player data dicts
            output_path: Optional file path to save PDF
            
        Returns:
            bytes: PDF file content
        """
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        
        # Background
        c.setFillColor(self.HEAT_BLACK)
        c.rect(0, 0, self.page_width, self.page_height, fill=1)
        
        # Title
        c.setFillColor(self.HEAT_RED)
        c.rect(0, self.page_height - 60, self.page_width, 60, fill=1)
        
        c.setFillColor(self.HEAT_WHITE)
        c.setFont("Helvetica-Bold", 28)
        c.drawCentredString(self.page_width / 2, self.page_height - 40, "PLAYER COMPARISON")
        
        # Calculate column width
        num_players = len(players_data)
        if num_players == 0:
            c.showPage()
            c.save()
            return buffer.getvalue()
        
        col_width = (self.page_width - 100) / num_players
        
        # Player columns
        x_start = 50
        y_position = self.page_height - 100
        
        for i, player in enumerate(players_data):
            x = x_start + (i * col_width)
            
            # Player name
            c.setFont("Helvetica-Bold", 14)
            c.setFillColor(self.HEAT_RED)
            player_name = player.get('player_name', 'UNKNOWN')
            if len(player_name) > 15:
                player_name = player_name[:12] + '...'
            c.drawCentredString(x + col_width/2, y_position, player_name.upper())
            
            # Cog score
            c.setFont("Helvetica-Bold", 36)
            c.setFillColor(self.HEAT_WHITE)
            cog_score = player.get('cog_score', 0.0)
            c.drawCentredString(x + col_width/2, y_position - 40, f"{cog_score:.1f}")
            
            # Vertical line separator (except for last column)
            if i < num_players - 1:
                c.setStrokeColor(self.HEAT_GRAY)
                c.setLineWidth(1)
                c.line(x + col_width, y_position, x + col_width, 100)
        
        # Category comparison
        y_position -= 100
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(self.HEAT_RED)
        c.drawString(50, y_position, "CATEGORIES")
        
        y_position -= 25
        
        # Get all categories
        all_categories = set()
        for player in players_data:
            all_categories.update(player.get('category_scores', {}).keys())
        
        for category in sorted(all_categories):
            c.setFont("Helvetica", 10)
            c.setFillColor(self.HEAT_WHITE)
            c.drawString(50, y_position, category[:20])
            
            # Draw scores for each player
            for i, player in enumerate(players_data):
                x = x_start + (i * col_width)
                score = player.get('category_scores', {}).get(category, 0.0)
                
                c.setFont("Helvetica-Bold", 10)
                c.drawCentredString(x + col_width/2, y_position, f"{score:.1f}")
            
            y_position -= 18
            
            if y_position < 120:
                break
        
        # Footer
        c.setFont("Helvetica", 10)
        c.setFillColor(self.HEAT_GRAY)
        c.drawCentredString(
            self.page_width / 2, 
            30, 
            f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | IntegrityHoops Analytics"
        )
        
        c.showPage()
        c.save()
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        # Save to file if path provided
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)
            logger.info(f"Comparison card saved to {output_path}")
        
        return pdf_bytes

