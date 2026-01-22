"""
Google Sheets builder module for Ising Quant System.
Creates and configures spreadsheets with formulas and formatting.
"""

from typing import Any, Optional

from googleapiclient.discovery import Resource

from ising_quant.config import Config
from ising_quant.google_auth import get_sheets_service


class SheetsBuilder:
    """Builder for creating and configuring Ising Quant spreadsheets."""

    def __init__(self, service: Optional[Resource] = None, config: Optional[Config] = None):
        """
        Initialize sheets builder.

        Args:
            service: Authenticated Sheets service. If None, creates from config.
            config: Configuration object. If None, creates new Config.
        """
        self.config = config or Config()
        self.service = service or get_sheets_service(self.config)

    def create_spreadsheet(self, title: str = "Ising Quant System") -> str:
        """
        Create a new spreadsheet with all tabs and formulas.

        Args:
            title: Title for the new spreadsheet.

        Returns:
            Spreadsheet ID of the created sheet.
        """
        # Create spreadsheet with proper locale and timezone
        spreadsheet_body = {
            "properties": {
                "title": title,
                "locale": "pt_BR",
                "timeZone": "America/Sao_Paulo",
            },
            "sheets": [
                {"properties": {"title": "IsingThermometer", "gridProperties": {"frozenRowCount": 0}}},
                {"properties": {"title": "DailyData", "gridProperties": {"frozenRowCount": 1}}},
                {"properties": {"title": "PortfolioSummary", "gridProperties": {"frozenRowCount": 1}}},
                {"properties": {"title": "Sinais", "gridProperties": {"frozenRowCount": 1}}},
                {"properties": {"title": "RiskLab", "gridProperties": {"frozenRowCount": 1}}},
                {"properties": {"title": "IsingAllocator", "gridProperties": {"frozenRowCount": 9}}},
            ],
        }

        spreadsheet = self.service.spreadsheets().create(body=spreadsheet_body).execute()
        spreadsheet_id = spreadsheet["spreadsheetId"]

        print(f"Created spreadsheet: {title}")
        print(f"Spreadsheet ID: {spreadsheet_id}")
        print(f"URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")

        # Apply formulas and formatting
        self.apply_all_formulas(spreadsheet_id)

        return spreadsheet_id

    def apply_all_formulas(self, spreadsheet_id: str):
        """
        Apply all formulas and formatting to an existing spreadsheet.

        Args:
            spreadsheet_id: ID of the spreadsheet to update.
        """
        print("Applying formulas and formatting...")

        # Apply formulas for each tab
        self._apply_ising_thermometer(spreadsheet_id)
        self._apply_daily_data(spreadsheet_id)
        self._apply_portfolio_summary(spreadsheet_id)
        self._apply_sinais(spreadsheet_id)
        self._apply_risk_lab(spreadsheet_id)
        self._apply_ising_allocator(spreadsheet_id)

        # Apply formatting
        self._apply_formatting(spreadsheet_id)

        print("Formulas and formatting applied successfully!")

    def _apply_ising_thermometer(self, spreadsheet_id: str):
        """Apply formulas to IsingThermometer tab."""
        formulas = [
            ['=GOOGLEFINANCE("INDEXCBOE:VIX")'],
            ['=GOOGLEFINANCE("USDBRL")'],
            ['=DESVPAD(QUERY(GOOGLEFINANCE("USDBRL";"price";HOJE()-45;HOJE());"select Col2 offset 1"))*RAIZ(252)'],
            ['=1/((A1/25) + (A3*8))'],
            ['=TANH(1/A4)'],
            ['=SE(A5>0,7; "CRASH (CAIXA)"; SE(A5>0,3; "ALERTA (DEFESA)"; "NORMAL (COMPRA)"))'],
        ]

        body = {"values": formulas}
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range="IsingThermometer!A1:A6",
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()

    def _apply_daily_data(self, spreadsheet_id: str):
        """Apply headers and formulas to DailyData tab."""
        # Headers
        headers = [["Data", "Ativo", "Preço Unitário", "Quantidade", "Valor Total", "Notas"]]

        body = {"values": headers}
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range="DailyData!A1:F1",
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()

        # Formula for row 2 (example)
        formulas = [
            [
                "",  # A2: Date (manual entry)
                "",  # B2: Asset (manual entry)
                '=SE(B2="Tesouro IPCA+ 2035"; TESOURO_DIRETO(B2); GOOGLEFINANCE(B2))',  # C2
                "",  # D2: Quantity (manual entry)
                "=C2*D2",  # E2
                "",  # F2: Notes (manual entry)
            ]
        ]

        body = {"values": formulas}
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range="DailyData!A2:F2",
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()

    def _apply_portfolio_summary(self, spreadsheet_id: str):
        """Apply headers and formulas to PortfolioSummary tab."""
        # Headers
        headers = [["Data", "Patrimônio Bruto", "Lucro Diário (R$)", "Retorno Log (%)", "Lucro Acumulado", "Drawdown"]]

        body = {"values": headers}
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range="PortfolioSummary!A1:F1",
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()

        # Row 2 formulas
        formulas = [
            [
                "=SORT(UNIQUE(DailyData!A2:A))",
                "=SE(A2=\"\";;SOMA.SE(DailyData!A:A; A2; DailyData!E:E))",
                "=SE(A2=\"\";;0)",
                "=SE(A2=\"\";;0)",
                "=SE(A2=\"\";;SOMA($C$2:C2))",
                "=SE(A2=\"\";;B2/MÁXIMO($B$2:B2)-1)",
            ]
        ]

        body = {"values": formulas}
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range="PortfolioSummary!A2:F2",
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()

        # Row 3 formulas (drag down pattern)
        formulas = [
            [
                "",  # Auto-filled from A2
                "=SE(A3=\"\";;SOMA.SE(DailyData!A:A; A3; DailyData!E:E))",
                "=SE(A3=\"\";;B3-B2)",
                "=SE(A3=\"\";;LN(B3/B2))",
                "=SE(A3=\"\";;SOMA($C$2:C3))",
                "=SE(A3=\"\";;B3/MÁXIMO($B$2:B3)-1)",
            ]
        ]

        body = {"values": formulas}
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range="PortfolioSummary!A3:F3",
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()

    def _apply_sinais(self, spreadsheet_id: str):
        """Apply headers and formulas to Sinais tab."""
        # Headers
        headers = [["Ativo", "Preço", "Média 20d", "DesvioPad 20d", "Z-Score", "Decisão", "Regime Ising", "Decisão Ajustada"]]

        body = {"values": headers}
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range="Sinais!A1:H1",
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()

        # Sample data and formulas
        data = [
            [
                "ABEV3",
                "=GOOGLEFINANCE(A2)",
                '=MÉDIA(QUERY(GOOGLEFINANCE(A2; "price"; HOJE()-30; HOJE()); "select Col2 limit 20"))',
                '=DESVPAD(QUERY(GOOGLEFINANCE(A2; "price"; HOJE()-30; HOJE()); "select Col2 limit 20"))',
                "=(B2-C2)/D2",
                '=SE(E2<-2;"COMPRA FORTE"; SE(E2>2;"VENDA"; "NEUTRO"))',
                "=IsingThermometer!A6",
                '=SE(A2="";""; SE(PROCURAR("CRASH";G2)>0;"NÃO COMPRAR (CRASH)"; SE(PROCURAR("ALERTA";G2)>0; SE(SEERRO(PROCV(A2;IsingAllocator!$J$2:$K$200;2;FALSO);"")="Tech";"EVITAR TECH (ALERTA)";F2); F2)))',
            ],
            [
                "AAPL34",
                "=GOOGLEFINANCE(A3)",
                '=MÉDIA(QUERY(GOOGLEFINANCE(A3; "price"; HOJE()-30; HOJE()); "select Col2 limit 20"))',
                '=DESVPAD(QUERY(GOOGLEFINANCE(A3; "price"; HOJE()-30; HOJE()); "select Col2 limit 20"))',
                "=(B3-C3)/D3",
                '=SE(E3<-2;"COMPRA FORTE"; SE(E3>2;"VENDA"; "NEUTRO"))',
                "=IsingThermometer!A6",
                '=SE(A3="";""; SE(PROCURAR("CRASH";G3)>0;"NÃO COMPRAR (CRASH)"; SE(PROCURAR("ALERTA";G3)>0; SE(SEERRO(PROCV(A3;IsingAllocator!$J$2:$K$200;2;FALSO);"")="Tech";"EVITAR TECH (ALERTA)";F3); F3)))',
            ],
            [
                "MSFT34",
                "=GOOGLEFINANCE(A4)",
                '=MÉDIA(QUERY(GOOGLEFINANCE(A4; "price"; HOJE()-30; HOJE()); "select Col2 limit 20"))',
                '=DESVPAD(QUERY(GOOGLEFINANCE(A4; "price"; HOJE()-30; HOJE()); "select Col2 limit 20"))',
                "=(B4-C4)/D4",
                '=SE(E4<-2;"COMPRA FORTE"; SE(E4>2;"VENDA"; "NEUTRO"))',
                "=IsingThermometer!A6",
                '=SE(A4="";""; SE(PROCURAR("CRASH";G4)>0;"NÃO COMPRAR (CRASH)"; SE(PROCURAR("ALERTA";G4)>0; SE(SEERRO(PROCV(A4;IsingAllocator!$J$2:$K$200;2;FALSO);"")="Tech";"EVITAR TECH (ALERTA)";F4); F4)))',
            ],
        ]

        body = {"values": data}
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range="Sinais!A2:H4",
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()

    def _apply_risk_lab(self, spreadsheet_id: str):
        """Apply headers and structure to RiskLab tab."""
        # Input table headers
        headers = [["Ticker", "Peso%", "Retorno Esp (Anual)", "Volatilidade (σ anual)"]]

        body = {"values": headers}
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range="RiskLab!A1:D1",
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()

        # Sample input data with volatility formulas
        inputs = [
            ["IPCA+ 2035", 0.30, 0.12, '=SEERRO(CALC_VOL(FILTER(DailyData!C:C; DailyData!B:B=A2)); 0,05)'],
            ["ABEV3", 0.25, 0.15, '=SEERRO(CALC_VOL(FILTER(DailyData!C:C; DailyData!B:B=A3)); 0,20)'],
            ["AAPL34", 0.25, 0.20, '=SEERRO(CALC_VOL(FILTER(DailyData!C:C; DailyData!B:B=A4)); 0,25)'],
            ["USD/Ouro", 0.10, 0.05, '=SEERRO(CALC_VOL(FILTER(DailyData!C:C; DailyData!B:B=A5)); 0,15)'],
            ["CDB", 0.10, 0.11, 0.05],
        ]

        body = {"values": inputs}
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range="RiskLab!A2:D6",
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()

        # Output labels and formulas
        outputs = [
            ["Valor da Carteira (R$)", 100000],
            ["Retorno Esperado", "=SOMARPRODUTO(B2:B6; C2:C6)"],
            ["Variância", "=MATRIZ.MULT(MATRIZ.MULT(TRANSPOR(B2:B6); G10:K14); B2:B6)"],
            ["Volatilidade (σ)", "=RAIZ(B11)"],
            ["VaR 95% (R$)", "=-INV.NORM(0,05; B10/252; B12/RAIZ(252)) * B9"],
            ["Sharpe Ratio", "=(B10 - B15)/B12"],
            ["Taxa Livre Risco", 0.10],
        ]

        body = {"values": outputs}
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range="RiskLab!A9:B15",
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()

    def _apply_ising_allocator(self, spreadsheet_id: str):
        """Apply formulas to IsingAllocator tab."""
        # Control panel
        panel = [
            ["Magnetização Atual", "=IsingThermometer!A5"],
            ["Regime", '=SE(B1>0,7;"CRASH";SE(B1>0,3;"ALERTA";"NORMAL"))'],
            ["Modo Alocação", "DISCRETO"],
            ["Aporte Mensal (R$)", 5000],
            ["Patrimônio Atual", "=SEERRO(LOOKUP(2;1/(PortfolioSummary!B2:B<>\"\");PortfolioSummary!B2:B);0)"],
            ["Última Atualização", "=MÁXIMO(DailyData!A2:A)"],
            ["Lambda (Contínuo)", "=MIN(1;MAX(0;(B1-0,3)/0,4))"],
        ]

        body = {"values": panel}
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range="IsingAllocator!A1:B7",
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()

        # Allocation table headers
        alloc_headers = [
            ["Bucket", "Peso NORMAL", "Peso ALERTA", "Peso CRASH", "Peso Target", 
             "Aporte Target (R$)", "Valor Atual (R$)", "Diferença (R$)", "Ação"]
        ]

        body = {"values": alloc_headers}
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range="IsingAllocator!A9:I9",
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()

        # Allocation data with formulas
        alloc_data = [
            [
                "Tesouro IPCA+ 2035", 0.20, 0.30, 0.50,
                '=SE($B$3="DISCRETO"; SE($B$2="NORMAL"; B10; SE($B$2="ALERTA"; C10; D10)); B10*(1-$B$7) + C10*($B$7)*(1-MIN(1;($B$1-0,7)/0,2)) + D10*MIN(1;($B$1-0,7)/0,2))',
                "=$B$4*E10",
                '=SEERRO(SOMARPRODUTO((PROCV($J$2:$J$200; $J$2:$K$200; 2; FALSO)=A10) * 1); 0)',
                "=F10-G10",
                '=SE(H10>0; "COMPRAR " & TEXTO(H10;"R$ #.##0,00"); SE(H10<-100; "VENDER " & TEXTO(-H10;"R$ #.##0,00"); "MANTER"))',
            ],
            [
                "CDBs", 0.15, 0.25, 0.30,
                '=SE($B$3="DISCRETO"; SE($B$2="NORMAL"; B11; SE($B$2="ALERTA"; C11; D11)); B11*(1-$B$7) + C11*($B$7)*(1-MIN(1;($B$1-0,7)/0,2)) + D11*MIN(1;($B$1-0,7)/0,2))',
                "=$B$4*E11",
                '=SEERRO(SOMARPRODUTO((PROCV($J$2:$J$200; $J$2:$K$200; 2; FALSO)=A11) * 1); 0)',
                "=F11-G11",
                '=SE(H11>0; "COMPRAR " & TEXTO(H11;"R$ #.##0,00"); SE(H11<-100; "VENDER " & TEXTO(-H11;"R$ #.##0,00"); "MANTER"))',
            ],
            [
                "FX Hedge (USD/EUR)", 0.05, 0.15, 0.15,
                '=SE($B$3="DISCRETO"; SE($B$2="NORMAL"; B12; SE($B$2="ALERTA"; C12; D12)); B12*(1-$B$7) + C12*($B$7)*(1-MIN(1;($B$1-0,7)/0,2)) + D12*MIN(1;($B$1-0,7)/0,2))',
                "=$B$4*E12",
                '=SEERRO(SOMARPRODUTO((PROCV($J$2:$J$200; $J$2:$K$200; 2; FALSO)=A12) * 1); 0)',
                "=F12-G12",
                '=SE(H12>0; "COMPRAR " & TEXTO(H12;"R$ #.##0,00"); SE(H12<-100; "VENDER " & TEXTO(-H12;"R$ #.##0,00"); "MANTER"))',
            ],
            [
                "Bebidas", 0.30, 0.15, 0.00,
                '=SE($B$3="DISCRETO"; SE($B$2="NORMAL"; B13; SE($B$2="ALERTA"; C13; D13)); B13*(1-$B$7) + C13*($B$7)*(1-MIN(1;($B$1-0,7)/0,2)) + D13*MIN(1;($B$1-0,7)/0,2))',
                "=$B$4*E13",
                '=SEERRO(SOMARPRODUTO((PROCV($J$2:$J$200; $J$2:$K$200; 2; FALSO)=A13) * 1); 0)',
                "=F13-G13",
                '=SE(H13>0; "COMPRAR " & TEXTO(H13;"R$ #.##0,00"); SE(H13<-100; "VENDER " & TEXTO(-H13;"R$ #.##0,00"); "MANTER"))',
            ],
            [
                "Tech", 0.25, 0.10, 0.00,
                '=SE($B$3="DISCRETO"; SE($B$2="NORMAL"; B14; SE($B$2="ALERTA"; C14; D14)); B14*(1-$B$7) + C14*($B$7)*(1-MIN(1;($B$1-0,7)/0,2)) + D14*MIN(1;($B$1-0,7)/0,2))',
                "=$B$4*E14",
                '=SEERRO(SOMARPRODUTO((PROCV($J$2:$J$200; $J$2:$K$200; 2; FALSO)=A14) * 1); 0)',
                "=F14-G14",
                '=SE(H14>0; "COMPRAR " & TEXTO(H14;"R$ #.##0,00"); SE(H14<-100; "VENDER " & TEXTO(-H14;"R$ #.##0,00"); "MANTER"))',
            ],
            [
                "Caixa USD/T-Bills", 0.05, 0.05, 0.05,
                '=SE($B$3="DISCRETO"; SE($B$2="NORMAL"; B15; SE($B$2="ALERTA"; C15; D15)); B15*(1-$B$7) + C15*($B$7)*(1-MIN(1;($B$1-0,7)/0,2)) + D15*MIN(1;($B$1-0,7)/0,2))',
                "=$B$4*E15",
                '=SEERRO(SOMARPRODUTO((PROCV($J$2:$J$200; $J$2:$K$200; 2; FALSO)=A15) * 1); 0)',
                "=F15-G15",
                '=SE(H15>0; "COMPRAR " & TEXTO(H15;"R$ #.##0,00"); SE(H15<-100; "VENDER " & TEXTO(-H15;"R$ #.##0,00"); "MANTER"))',
            ],
        ]

        body = {"values": alloc_data}
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range="IsingAllocator!A10:I15",
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()

        # Ticker to Bucket mapping
        mapping_headers = [["Ticker", "Bucket"]]
        mapping_data = [
            ["Tesouro IPCA+ 2035", "Tesouro IPCA+ 2035"],
            ["CDB", "CDBs"],
            ["USD", "FX Hedge (USD/EUR)"],
            ["EUR", "FX Hedge (USD/EUR)"],
            ["ABEV3", "Bebidas"],
            ["AMBEV", "Bebidas"],
            ["AAPL34", "Tech"],
            ["MSFT34", "Tech"],
            ["GOOGL34", "Tech"],
            ["AMZN34", "Tech"],
            ["NVDA34", "Tech"],
            ["USD Cash", "Caixa USD/T-Bills"],
            ["T-Bills", "Caixa USD/T-Bills"],
        ]

        all_mapping = mapping_headers + mapping_data

        body = {"values": all_mapping}
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range="IsingAllocator!J1:K14",
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()

    def _apply_formatting(self, spreadsheet_id: str):
        """Apply number formatting to sheets."""
        requests = []

        # Get sheet IDs
        spreadsheet = self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = {sheet["properties"]["title"]: sheet["properties"]["sheetId"] 
                  for sheet in spreadsheet["sheets"]}

        # DailyData: Column A as Date, C and E as Currency
        if "DailyData" in sheets:
            requests.extend([
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheets["DailyData"],
                            "startColumnIndex": 0,
                            "endColumnIndex": 1,
                        },
                        "cell": {"userEnteredFormat": {"numberFormat": {"type": "DATE"}}},
                        "fields": "userEnteredFormat.numberFormat",
                    }
                },
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheets["DailyData"],
                            "startColumnIndex": 2,
                            "endColumnIndex": 3,
                        },
                        "cell": {"userEnteredFormat": {"numberFormat": {"type": "CURRENCY", "pattern": "R$ #,##0.00"}}},
                        "fields": "userEnteredFormat.numberFormat",
                    }
                },
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheets["DailyData"],
                            "startColumnIndex": 4,
                            "endColumnIndex": 5,
                        },
                        "cell": {"userEnteredFormat": {"numberFormat": {"type": "CURRENCY", "pattern": "R$ #,##0.00"}}},
                        "fields": "userEnteredFormat.numberFormat",
                    }
                },
            ])

        # PortfolioSummary: Formatting
        if "PortfolioSummary" in sheets:
            requests.extend([
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheets["PortfolioSummary"],
                            "startColumnIndex": 0,
                            "endColumnIndex": 1,
                        },
                        "cell": {"userEnteredFormat": {"numberFormat": {"type": "DATE"}}},
                        "fields": "userEnteredFormat.numberFormat",
                    }
                },
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheets["PortfolioSummary"],
                            "startColumnIndex": 1,
                            "endColumnIndex": 2,
                        },
                        "cell": {"userEnteredFormat": {"numberFormat": {"type": "CURRENCY", "pattern": "R$ #,##0.00"}}},
                        "fields": "userEnteredFormat.numberFormat",
                    }
                },
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheets["PortfolioSummary"],
                            "startColumnIndex": 2,
                            "endColumnIndex": 3,
                        },
                        "cell": {"userEnteredFormat": {"numberFormat": {"type": "CURRENCY", "pattern": "R$ #,##0.00"}}},
                        "fields": "userEnteredFormat.numberFormat",
                    }
                },
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheets["PortfolioSummary"],
                            "startColumnIndex": 3,
                            "endColumnIndex": 4,
                        },
                        "cell": {"userEnteredFormat": {"numberFormat": {"type": "PERCENT", "pattern": "0.00%"}}},
                        "fields": "userEnteredFormat.numberFormat",
                    }
                },
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheets["PortfolioSummary"],
                            "startColumnIndex": 4,
                            "endColumnIndex": 5,
                        },
                        "cell": {"userEnteredFormat": {"numberFormat": {"type": "CURRENCY", "pattern": "R$ #,##0.00"}}},
                        "fields": "userEnteredFormat.numberFormat",
                    }
                },
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheets["PortfolioSummary"],
                            "startColumnIndex": 5,
                            "endColumnIndex": 6,
                        },
                        "cell": {"userEnteredFormat": {"numberFormat": {"type": "PERCENT", "pattern": "0.00%"}}},
                        "fields": "userEnteredFormat.numberFormat",
                    }
                },
            ])

        # Execute all formatting requests
        if requests:
            body = {"requests": requests}
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id, body=body
            ).execute()
