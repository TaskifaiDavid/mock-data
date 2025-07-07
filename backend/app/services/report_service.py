import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from typing import Dict, Any, List, Optional
import io
import base64
from datetime import datetime
import logging
from app.services.db_service import DatabaseService
from app.utils.exceptions import AppException

logger = logging.getLogger(__name__)

class ReportService:
    def __init__(self):
        self.db_service = DatabaseService()
        
    async def generate_cleaning_report(
        self, 
        user_id: str, 
        upload_id: Optional[str] = None,
        format: str = "pdf"
    ) -> Dict[str, Any]:
        """
        Generate cleaning report for user data
        
        Args:
            user_id: User ID
            upload_id: Optional specific upload ID
            format: Output format (pdf, csv, excel)
            
        Returns:
            Dictionary with report data and metadata
        """
        try:
            # Get cleaned data
            cleaned_data = await self._get_cleaned_data(user_id, upload_id)
            
            # Calculate metadata
            metadata = await self._calculate_metadata(cleaned_data)
            
            # Generate report based on format
            if format.lower() == "pdf":
                report_data = self._generate_pdf_report(cleaned_data, metadata)
                content_type = "application/pdf"
            elif format.lower() == "csv":
                report_data = self._generate_csv_report(cleaned_data)
                content_type = "text/csv"
            elif format.lower() == "excel":
                report_data = self._generate_excel_report(cleaned_data, metadata)
                content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            else:
                raise AppException(f"Unsupported format: {format}", 400)
            
            # Encode as base64
            report_b64 = base64.b64encode(report_data).decode('utf-8')
            
            return {
                "filename": f"cleaning_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}",
                "data": report_b64,
                "content_type": content_type,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error generating cleaning report: {e}")
            raise AppException(f"Report generation failed: {str(e)}", 500)
    
    async def _get_cleaned_data(self, user_id: str, upload_id: Optional[str]) -> pd.DataFrame:
        """Get cleaned data from database"""
        try:
            if upload_id:
                query = """
                SELECT 
                    se.product_ean,
                    se.month,
                    se.year,
                    se.quantity,
                    se.sales_lc,
                    se.sales_eur,
                    se.currency,
                    se.reseller,
                    se.functional_name,
                    se.created_at,
                    u.filename,
                    u.uploaded_at
                FROM sellout_entries2 se
                JOIN uploads u ON se.upload_id = u.id
                WHERE u.user_id = %s AND u.id = %s
                ORDER BY se.created_at DESC
                """
                params = (user_id, upload_id)
            else:
                query = """
                SELECT 
                    se.product_ean,
                    se.month,
                    se.year,
                    se.quantity,
                    se.sales_lc,
                    se.sales_eur,
                    se.currency,
                    se.reseller,
                    se.functional_name,
                    se.created_at,
                    u.filename,
                    u.uploaded_at
                FROM sellout_entries2 se
                JOIN uploads u ON se.upload_id = u.id
                WHERE u.user_id = %s
                ORDER BY se.created_at DESC
                LIMIT 1000
                """
                params = (user_id,)
            
            result = await self.db_service.fetch_all(query, params)
            return pd.DataFrame(result)
            
        except Exception as e:
            logger.error(f"Error fetching cleaned data: {e}")
            raise AppException(f"Failed to fetch cleaned data: {str(e)}", 500)
    
    async def _calculate_metadata(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate report metadata"""
        try:
            metadata = {
                "cleanedRows": len(df),
                "totalValue": float(df['sales_eur'].sum()) if 'sales_eur' in df.columns else 0,
                "currency": "EUR",
                "uniqueProducts": df['product_ean'].nunique() if 'product_ean' in df.columns else 0,
                "uniqueResellers": df['reseller'].nunique() if 'reseller' in df.columns else 0,
                "dateRange": {
                    "from": df['created_at'].min().isoformat() if 'created_at' in df.columns and len(df) > 0 else None,
                    "to": df['created_at'].max().isoformat() if 'created_at' in df.columns and len(df) > 0 else None
                },
                "processingTime": None,  # Will be set by caller
                "generatedAt": datetime.now().isoformat()
            }
            
            # Add reseller breakdown
            if 'reseller' in df.columns and len(df) > 0:
                reseller_stats = df.groupby('reseller').agg({
                    'sales_eur': 'sum',
                    'quantity': 'sum'
                }).to_dict('index')
                metadata["resellerBreakdown"] = reseller_stats
                
            return metadata
            
        except Exception as e:
            logger.error(f"Error calculating metadata: {e}")
            return {"cleanedRows": 0, "totalValue": 0, "currency": "EUR"}
    
    def _generate_pdf_report(self, df: pd.DataFrame, metadata: Dict[str, Any]) -> bytes:
        """Generate PDF report"""
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.darkblue
            )
            story.append(Paragraph("Bibbi Cleaner Report", title_style))
            story.append(Spacer(1, 12))
            
            # Summary section
            summary_style = ParagraphStyle(
                'Summary',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=6
            )
            
            story.append(Paragraph(f"<b>Report Generated:</b> {metadata.get('generatedAt', 'N/A')}", summary_style))
            story.append(Paragraph(f"<b>Total Rows Cleaned:</b> {metadata.get('cleanedRows', 0)}", summary_style))
            story.append(Paragraph(f"<b>Total Value:</b> {metadata.get('totalValue', 0):.2f} {metadata.get('currency', 'EUR')}", summary_style))
            story.append(Paragraph(f"<b>Unique Products:</b> {metadata.get('uniqueProducts', 0)}", summary_style))
            story.append(Paragraph(f"<b>Unique Resellers:</b> {metadata.get('uniqueResellers', 0)}", summary_style))
            story.append(Spacer(1, 20))
            
            # Data table (first 50 rows)
            if len(df) > 0:
                story.append(Paragraph("Data Sample (First 50 Rows)", styles['Heading2']))
                story.append(Spacer(1, 12))
                
                # Prepare table data
                table_data = []
                headers = ['Product EAN', 'Month', 'Year', 'Quantity', 'Sales (EUR)', 'Reseller']
                table_data.append(headers)
                
                for _, row in df.head(50).iterrows():
                    table_data.append([
                        str(row.get('product_ean', '')),
                        str(row.get('month', '')),
                        str(row.get('year', '')),
                        str(row.get('quantity', '')),
                        f"{row.get('sales_eur', 0):.2f}",
                        str(row.get('reseller', ''))
                    ])
                
                # Create table
                table = Table(table_data, colWidths=[1.5*inch, 0.7*inch, 0.7*inch, 0.8*inch, 1*inch, 1.3*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                ]))
                story.append(table)
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            return buffer.read()
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            raise AppException(f"PDF generation failed: {str(e)}", 500)
    
    def _generate_csv_report(self, df: pd.DataFrame) -> bytes:
        """Generate CSV report"""
        try:
            buffer = io.StringIO()
            df.to_csv(buffer, index=False)
            buffer.seek(0)
            return buffer.getvalue().encode('utf-8')
            
        except Exception as e:
            logger.error(f"Error generating CSV report: {e}")
            raise AppException(f"CSV generation failed: {str(e)}", 500)
    
    def _generate_excel_report(self, df: pd.DataFrame, metadata: Dict[str, Any]) -> bytes:
        """Generate Excel report with multiple sheets"""
        try:
            buffer = io.BytesIO()
            
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                # Data sheet
                df.to_excel(writer, sheet_name='Cleaned Data', index=False)
                
                # Summary sheet
                summary_df = pd.DataFrame([
                    ['Total Rows Cleaned', metadata.get('cleanedRows', 0)],
                    ['Total Value (EUR)', metadata.get('totalValue', 0)],
                    ['Unique Products', metadata.get('uniqueProducts', 0)],
                    ['Unique Resellers', metadata.get('uniqueResellers', 0)],
                    ['Report Generated', metadata.get('generatedAt', 'N/A')]
                ], columns=['Metric', 'Value'])
                
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Reseller breakdown sheet
                if 'resellerBreakdown' in metadata:
                    reseller_df = pd.DataFrame.from_dict(
                        metadata['resellerBreakdown'], 
                        orient='index'
                    ).reset_index()
                    reseller_df.columns = ['Reseller', 'Sales (EUR)', 'Quantity']
                    reseller_df.to_excel(writer, sheet_name='Reseller Breakdown', index=False)
            
            buffer.seek(0)
            return buffer.read()
            
        except Exception as e:
            logger.error(f"Error generating Excel report: {e}")
            raise AppException(f"Excel generation failed: {str(e)}", 500)