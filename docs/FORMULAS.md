# Formula Reference - Ising Quant System

This document contains ALL formulas used in the Google Sheets, organized by tab.

**IMPORTANT**: All formulas use PT-BR (Brazilian Portuguese) function names with `;` as separator.

## TAB 1: IsingThermometer

Calculates market "temperature" (liquidity) and "magnetization" (crash probability).

| Cell | Label | Formula | Format |
|------|-------|---------|--------|
| **A1** | VIX (Medo Global) | `=GOOGLEFINANCE("INDEXCBOE:VIX")` | Number |
| **A2** | USD/BRL (Câmbio) | `=GOOGLEFINANCE("USDBRL")` | Currency |
| **A3** | Volatilidade USD (30d) | `=DESVPAD(QUERY(GOOGLEFINANCE("USDBRL";"price";HOJE()-45;HOJE());"select Col2 offset 1"))*RAIZ(252)` | Percentage |
| **A4** | Temperatura (T) | `=1/((A1/25) + (A3*8))` | Number (2 decimals) |
| **A5** | Magnetização (M) | `=TANH(1/A4)` | Number (2 decimals) |
| **A6** | STATUS MERCADO | `=SE(A5>0,7; "CRASH (CAIXA)"; SE(A5>0,3; "ALERTA (DEFESA)"; "NORMAL (COMPRA)"))` | Bold text |

**Explanation**:
- VIX and USD volatility represent market fear
- Temperature T combines both metrics
- Magnetization M = tanh(1/T) represents crash probability
- Status provides human-readable regime

---

## TAB 2: DailyData

Historical operations and daily prices. Headers in row 1, formulas start at row 2.

### Headers (Row 1)

| A | B | C | D | E | F |
|---|---|---|---|---|---|
| Data | Ativo | Preço Unitário | Quantidade | Valor Total | Notas |

### Formulas (Row 2, drag down)

| Column | Formula | Notes |
|--------|---------|-------|
| **A** | (Manual entry: 20/01/2026) | Date format |
| **B** | (Manual entry: ABEV3, Tesouro IPCA+ 2035, etc.) | Text |
| **C** | `=SE(B2="Tesouro IPCA+ 2035"; TESOURO_DIRETO(B2); GOOGLEFINANCE(B2))` | Currency format |
| **D** | (Manual entry: 2.5) | Number |
| **E** | `=C2*D2` | Currency format |
| **F** | (Manual notes) | Text |

**Configuration**:
- Freeze row 1 (View > Freeze > 1 row)
- Format column A as Date
- Format columns C and E as Currency (R$)

**Important**: For historical data, copy and "Paste values only" to prevent recalculation.

---

## TAB 3: PortfolioSummary

Automatic portfolio aggregation by date. All formulas use PT-BR syntax.

### Headers (Row 1)

| A | B | C | D | E | F |
|---|---|---|---|---|---|
| Data | Patrimônio Bruto | Lucro Diário (R$) | Retorno Log (%) | Lucro Acumulado | Drawdown |

### Row 2 Formulas

| Cell | Formula | Explanation |
|------|---------|-------------|
| **A2** | `=SORT(UNIQUE(DailyData!A2:A))` | Unique sorted dates from DailyData |
| **B2** | `=SE(A2="";;SOMA.SE(DailyData!A:A; A2; DailyData!E:E))` | Sum of values for this date |
| **C2** | `=SE(A2="";;0)` | First day has no profit (baseline) |
| **D2** | `=SE(A2="";;0)` | First day has no return |
| **E2** | `=SE(A2="";;SOMA($C$2:C2))` | Cumulative profit from start |
| **F2** | `=SE(A2="";;B2/MÁXIMO($B$2:B2)-1)` | Drawdown from peak |

### Row 3+ Formulas (drag down)

| Cell | Formula | Explanation |
|------|---------|-------------|
| **A[r]** | (Auto-filled from A2) | Next unique date |
| **B[r]** | `=SE(A[r]="";;SOMA.SE(DailyData!A:A; A[r]; DailyData!E:E))` | Portfolio value on date |
| **C[r]** | `=SE(A[r]="";;B[r]-B[r-1])` | Profit vs previous day |
| **D[r]** | `=SE(A[r]="";;LN(B[r]/B[r-1]))` | Log return |
| **E[r]** | `=SE(A[r]="";;SOMA($C$2:C[r]))` | Cumulative profit |
| **F[r]** | `=SE(A[r]="";;B[r]/MÁXIMO($B$2:B[r])-1)` | Current drawdown |

**Configuration**:
- Freeze row 1
- Format column A as Date
- Format column B as Currency
- Format columns C, E as Currency
- Format columns D, F as Percentage

---

## TAB 4: Sinais

Opportunity radar using Z-Score and momentum indicators.

### Headers (Row 1)

| A | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|
| Ativo | Preço | Média 20d | DesvioPad 20d | Z-Score | Decisão | Regime Ising | Decisão Ajustada |

### Row 2 Formulas (drag down)

| Cell | Formula | Explanation |
|------|---------|-------------|
| **A2** | (Manual: ABEV3, AAPL34, MSFT34, etc.) | Ticker symbol |
| **B2** | `=GOOGLEFINANCE(A2)` | Current price |
| **C2** | `=MÉDIA(QUERY(GOOGLEFINANCE(A2; "price"; HOJE()-30; HOJE()); "select Col2 limit 20"))` | 20-day average |
| **D2** | `=DESVPAD(QUERY(GOOGLEFINANCE(A2; "price"; HOJE()-30; HOJE()); "select Col2 limit 20"))` | 20-day std dev |
| **E2** | `=(B2-C2)/D2` | Z-Score calculation |
| **F2** | `=SE(E2<-2;"COMPRA FORTE"; SE(E2>2;"VENDA"; "NEUTRO"))` | Basic signal |
| **G2** | `=IsingThermometer!A6` | Market regime from thermometer |
| **H2** | `=SE(A2="";""; SE(G2="CRASH (CAIXA)";"NÃO COMPRAR (CRASH)"; SE(PROCURAR("ALERTA";G2)>0; SE(SEERRO(PROCV(A2;IsingAllocator!$J$2:$K$200;2;FALSO);"")="Tech";"EVITAR TECH (ALERTA)";F2); F2)))` | Adjusted by regime |

**Sample Tickers** (populate A2:A20):
- Brazilian: ABEV3, PETR4, VALE3, ITUB4, BBDC4, MGLU3, B3SA3
- US ADRs: AAPL34, MSFT34, GOOGL34, AMZN34, NVDA34
- Commodities: Use tickers like GLD, SLV (via GOOGLEFINANCE)

**Configuration**:
- Freeze row 1
- Format column B as Currency
- Format column E as Number (2 decimals)

---

## TAB 5: RiskLab

Portfolio risk calculation with correlation matrix.

### Input Table (A1:D6)

| Row | A (Ticker) | B (Peso %) | C (Retorno Esp. Anual) | D (Volatilidade σ anual) |
|-----|-----------|------------|------------------------|--------------------------|
| 1 | Ticker | Peso% | Retorno Esp (Anual) | Volatilidade (σ anual) |
| 2 | IPCA+ 2035 | 0,30 | 0,12 | `=SEERRO(CALC_VOL(FILTER(DailyData!C:C; DailyData!B:B=A2)); 0,05)` |
| 3 | ABEV3 | 0,25 | 0,15 | `=SEERRO(CALC_VOL(FILTER(DailyData!C:C; DailyData!B:B=A3)); 0,20)` |
| 4 | AAPL34 | 0,25 | 0,20 | `=SEERRO(CALC_VOL(FILTER(DailyData!C:C; DailyData!B:B=A4)); 0,25)` |
| 5 | USD/Ouro | 0,10 | 0,05 | `=SEERRO(CALC_VOL(FILTER(DailyData!C:C; DailyData!B:B=A5)); 0,15)` |
| 6 | CDB | 0,10 | 0,11 | 0,05 |

### Correlation Matrix (Manual Entry G3:K7)

Example correlation matrix (5x5):
```
        IPCA  ABEV  AAPL  USD   CDB
IPCA    1.00 -0.10 -0.20  0.30  0.80
ABEV   -0.10  1.00  0.40 -0.15 -0.05
AAPL   -0.20  0.40  1.00  0.10  0.00
USD     0.30 -0.15  0.10  1.00  0.20
CDB     0.80 -0.05  0.00  0.20  1.00
```

Place correlation values in G3:K7.

### Covariance Matrix (G10:K14)

Formula for each cell (example for G10):
```
=G3 * $D2 * D$2
```

Drag to fill entire covariance matrix G10:K14.

### Portfolio Outputs

| Cell | Label | Formula | Explanation |
|------|-------|---------|-------------|
| **B8** | Label | "Valor da Carteira (R$)" | - |
| **B9** | Input | 100000 | Manual input: portfolio value |
| **B10** | Retorno Esperado | `=SOMARPRODUTO(B2:B6; C2:C6)` | Weighted return |
| **B11** | Variância | `=MATRIZ.MULT(MATRIZ.MULT(TRANSPOR(B2:B6); G10:K14); B2:B6)` | Portfolio variance |
| **B12** | Volatilidade (σ) | `=RAIZ(B11)` | Portfolio std dev |
| **B13** | VaR 95% (R$) | `=-INV.NORM(0,05; B10/252; B12/RAIZ(252)) * B9` | Daily VaR |
| **B15** | Taxa Livre Risco | 0,10 | Manual input |
| **B14** | Sharpe Ratio | `=(B10 - B15)/B12` | Risk-adjusted return |

**Configuration**:
- Format B9, B13 as Currency
- Format B10, B12, B15 as Percentage
- Format B14 as Number (2 decimals)

---

## TAB 6: IsingAllocator

Dynamic allocation based on Ising market regime.

### Control Panel (A1:B7)

| Cell | Label | Formula/Value |
|------|-------|---------------|
| **A1** | "Magnetização Atual" | - |
| **B1** | | `=IsingThermometer!A5` |
| **A2** | "Regime" | - |
| **B2** | | `=SE(B1>0,7;"CRASH";SE(B1>0,3;"ALERTA";"NORMAL"))` |
| **A3** | "Modo Alocação" | - |
| **B3** | | "DISCRETO" or "CONTINUO" (manual input) |
| **A4** | "Aporte Mensal (R$)" | - |
| **B4** | | 5000 (manual input) |
| **A5** | "Patrimônio Atual" | - |
| **B5** | | `=SEERRO(LOOKUP(2;1/(PortfolioSummary!B2:B<>"");PortfolioSummary!B2:B);0)` |
| **A6** | "Última Atualização" | - |
| **B6** | | `=MÁXIMO(DailyData!A2:A)` |
| **A7** | "Lambda (Contínuo)" | - |
| **B7** | | `=MIN(1;MAX(0;(B1-0,3)/0,4))` |

### Allocation Table (A9:I15)

Headers (Row 9):
| A | B | C | D | E | F | G | H | I |
|---|---|---|---|---|---|---|---|---|
| Bucket | Peso NORMAL | Peso ALERTA | Peso CRASH | Peso Target | Aporte Target (R$) | Valor Atual (R$) | Diferença (R$) | Ação |

Rows 10-15 (example):

**Row 10 - Tesouro IPCA+ 2035**:
```
A10: Tesouro IPCA+ 2035
B10: 0,20
C10: 0,30
D10: 0,50
E10: =SE($B$3="DISCRETO"; SE($B$2="NORMAL"; B10; SE($B$2="ALERTA"; C10; D10)); B10*(1-$B$7) + C10*($B$7)*(1-MIN(1;($B$1-0,7)/0,2)) + D10*MIN(1;($B$1-0,7)/0,2))
F10: =$B$4*E10
G10: =SOMARPRODUTO((PROCV($J$2:$J$200; $J$2:$K$200; 2; FALSO)=A10) * 1; PROCV(DailyData!$B$2:$B; DailyData!$A$2:$E; 5; FALSO))
H10: =F10-G10
I10: =SE(H10>0; "COMPRAR " & TEXTO(H10;"R$ #.##0,00"); SE(H10<-100; "VENDER " & TEXTO(-H10;"R$ #.##0,00"); "MANTER"))
```

**Row 11 - CDBs**:
```
A11: CDBs
B11: 0,15
C11: 0,25
D11: 0,30
E11: [Same formula as E10]
F11: [Same formula as F10]
G11: [Same formula as G10]
H11: [Same formula as H10]
I11: [Same formula as I10]
```

**Row 12 - FX Hedge (USD/EUR)**:
```
A12: FX Hedge (USD/EUR)
B12: 0,05
C12: 0,15
D12: 0,15
E12: [Same formula as E10]
F12: [Same formula as F10]
G12: [Same formula as G10]
H12: [Same formula as H10]
I12: [Same formula as I10]
```

**Row 13 - Bebidas (ABEV3)**:
```
A13: Bebidas
B13: 0,30
C13: 0,15
D13: 0,00
E13: [Same formula as E10]
F13: [Same formula as F10]
G13: [Same formula as G10]
H13: [Same formula as H10]
I13: [Same formula as I10]
```

**Row 14 - Tech (AAPL/MSFT)**:
```
A14: Tech
B14: 0,25
C14: 0,10
D14: 0,00
E14: [Same formula as E10]
F14: [Same formula as F10]
G14: [Same formula as G10]
H14: [Same formula as H10]
I14: [Same formula as I10]
```

**Row 15 - Caixa USD/T-Bills**:
```
A15: Caixa USD/T-Bills
B15: 0,05
C15: 0,05
D15: 0,05
E15: [Same formula as E10]
F15: [Same formula as F10]
G15: [Same formula as G10]
H15: [Same formula as H10]
I15: [Same formula as I10]
```

### Ticker to Bucket Mapping (J1:K200)

Headers (Row 1):
| J | K |
|---|---|
| Ticker | Bucket |

Example mappings (J2:K20):
```
J2: Tesouro IPCA+ 2035    K2: Tesouro IPCA+ 2035
J3: CDB                   K3: CDBs
J4: USD                   K4: FX Hedge (USD/EUR)
J5: EUR                   K5: FX Hedge (USD/EUR)
J6: ABEV3                 K6: Bebidas
J7: AMBEV                 K7: Bebidas
J8: AAPL34                K8: Tech
J9: MSFT34                K9: Tech
J10: GOOGL34              K10: Tech
J11: AMZN34               K11: Tech
J12: NVDA34               K12: Tech
J13: USD Cash             K13: Caixa USD/T-Bills
J14: T-Bills              K14: Caixa USD/T-Bills
... (continue as needed)
```

**Configuration**:
- Freeze row 1 in allocation table
- Format columns B-E as Percentage
- Format columns F-H as Currency
- Conditional formatting: Highlight row if Regime = "CRASH" (red)

---

## Apps Script Custom Functions

These functions must be implemented in Apps Script (see apps_script/Code.gs).

### TESOURO_DIRETO(nome_titulo)

Fetches current price from Tesouro Direto API.

**Usage**:
```
=TESOURO_DIRETO("Tesouro IPCA+ 2035")
```

### CALC_VOL(prices_range)

Calculates annualized volatility from price range.

**Usage**:
```
=CALC_VOL(A2:A100)
```

### Z_SCORE(current_price, history_range)

Calculates Z-Score from current price and historical range.

**Usage**:
```
=Z_SCORE(100; A2:A100)
```

---

## Notes

1. **All formulas use PT-BR syntax**: Function names in Portuguese with `;` separator
2. **Common translations**:
   - IF → SE
   - SUM → SOMA
   - AVERAGE → MÉDIA
   - STDEV → DESVPAD
   - SQRT → RAIZ
   - MAX → MÁXIMO
   - MIN → MÍNIMO
   - LN → LN (same)
   - VLOOKUP → PROCV
   - SUMIF → SOMA.SE
   - SUMPRODUCT → SOMARPRODUTO
   - MMULT → MATRIZ.MULT
   - TRANSPOSE → TRANSPOR
   - IFERROR → SEERRO
   - TODAY → HOJE
   - FILTER → FILTER (same)
   - SEARCH → PROCURAR
   - TEXT → TEXTO

3. **Important**: Copy formulas exactly as shown, including spacing and semicolons.

4. **Testing**: Always test formulas in a blank cell first before applying to entire columns.

5. **Performance**: For large datasets, consider using "Paste values only" for historical data to prevent constant recalculation.
