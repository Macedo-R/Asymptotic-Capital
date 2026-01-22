/**
 * Ising Quant System - Custom Functions for Google Sheets
 * 
 * This script provides custom functions to enhance the quantitative trading system:
 * - TESOURO_DIRETO: Fetch Brazilian Treasury bond prices
 * - CALC_VOL: Calculate annualized volatility
 * - Z_SCORE: Calculate statistical Z-Score
 * 
 * @author Ising Quant System
 * @version 1.0.0
 */

// ============================================================================
// CONFIGURATION
// ============================================================================

/** Cache duration in seconds (5 minutes) */
const CACHE_DURATION = 300;

/** Tesouro Direto API endpoint */
const TESOURO_API = "https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PrecoTaxaTesouroDireto.csv";

// ============================================================================
// CUSTOM FUNCTIONS
// ============================================================================

/**
 * Fetches the current price of a Brazilian Treasury bond (Tesouro Direto).
 * 
 * @param {string} nomeTitulo - Name of the treasury bond (e.g., "Tesouro IPCA+ 2035")
 * @return {number} Current unit price of the bond, or 0 if not found
 * @customfunction
 * 
 * @example
 * =TESOURO_DIRETO("Tesouro IPCA+ 2035")
 */
function TESOURO_DIRETO(nomeTitulo) {
  if (!nomeTitulo || typeof nomeTitulo !== 'string') {
    return 0;
  }
  
  // Try to get from cache first
  var cache = CacheService.getScriptCache();
  var cacheKey = 'tesouro_' + nomeTitulo.replace(/\s+/g, '_');
  var cached = cache.get(cacheKey);
  
  if (cached !== null) {
    return parseFloat(cached);
  }
  
  try {
    // Fetch Tesouro Direto CSV data
    var response = UrlFetchApp.fetch(TESOURO_API);
    var csv = response.getContentText('ISO-8859-1'); // Tesouro uses Latin-1 encoding
    var lines = csv.split('\n');
    
    if (lines.length < 2) {
      Logger.log('TESOURO_DIRETO: CSV vazio ou inválido');
      return 0;
    }
    
    // Parse CSV header
    var headers = lines[0].split(';');
    var nomeIndex = headers.indexOf('Tipo Titulo');
    var precoIndex = headers.indexOf('PU Compra Manha');
    
    if (nomeIndex === -1 || precoIndex === -1) {
      Logger.log('TESOURO_DIRETO: Colunas não encontradas no CSV');
      return 0;
    }
    
    // Search for the bond
    for (var i = 1; i < lines.length; i++) {
      var cols = lines[i].split(';');
      if (cols.length <= Math.max(nomeIndex, precoIndex)) continue;
      
      var titulo = cols[nomeIndex].trim();
      if (titulo.indexOf(nomeTitulo) !== -1 || nomeTitulo.indexOf(titulo) !== -1) {
        var preco = cols[precoIndex].trim().replace(',', '.');
        var precoNum = parseFloat(preco);
        
        if (!isNaN(precoNum) && precoNum > 0) {
          // Cache the result
          cache.put(cacheKey, precoNum.toString(), CACHE_DURATION);
          return precoNum;
        }
      }
    }
    
    Logger.log('TESOURO_DIRETO: Título não encontrado: ' + nomeTitulo);
    return 0;
    
  } catch (error) {
    Logger.log('TESOURO_DIRETO: Erro ao buscar dados: ' + error.toString());
    return 0;
  }
}

/**
 * Calculates annualized volatility from a range of prices.
 * Uses log returns and annualizes with sqrt(252) for trading days.
 * 
 * @param {range} pricesRange - Range of prices (single column)
 * @return {number} Annualized volatility (standard deviation)
 * @customfunction
 * 
 * @example
 * =CALC_VOL(A2:A100)
 */
function CALC_VOL(pricesRange) {
  if (!pricesRange || !Array.isArray(pricesRange)) {
    return 0;
  }
  
  // Flatten the range and filter valid numbers
  var prices = [];
  for (var i = 0; i < pricesRange.length; i++) {
    var row = pricesRange[i];
    var value = Array.isArray(row) ? row[0] : row;
    
    if (typeof value === 'number' && !isNaN(value) && value > 0) {
      prices.push(value);
    }
  }
  
  if (prices.length < 2) {
    Logger.log('CALC_VOL: Dados insuficientes (mínimo 2 preços)');
    return 0;
  }
  
  try {
    // Calculate log returns
    var logReturns = [];
    for (var i = 1; i < prices.length; i++) {
      var logReturn = Math.log(prices[i] / prices[i - 1]);
      if (!isNaN(logReturn) && isFinite(logReturn)) {
        logReturns.push(logReturn);
      }
    }
    
    if (logReturns.length < 2) {
      Logger.log('CALC_VOL: Log returns insuficientes');
      return 0;
    }
    
    // Calculate mean
    var mean = 0;
    for (var i = 0; i < logReturns.length; i++) {
      mean += logReturns[i];
    }
    mean /= logReturns.length;
    
    // Calculate variance
    var variance = 0;
    for (var i = 0; i < logReturns.length; i++) {
      var diff = logReturns[i] - mean;
      variance += diff * diff;
    }
    variance /= (logReturns.length - 1); // Sample variance
    
    // Calculate standard deviation
    var stdDev = Math.sqrt(variance);
    
    // Annualize (252 trading days)
    var annualizedVol = stdDev * Math.sqrt(252);
    
    return annualizedVol;
    
  } catch (error) {
    Logger.log('CALC_VOL: Erro no cálculo: ' + error.toString());
    return 0;
  }
}

/**
 * Calculates the Z-Score (standard score) of a current price relative to historical prices.
 * Z-Score = (current - mean) / std_dev
 * 
 * @param {number} currentPrice - Current price to evaluate
 * @param {range} historyRange - Range of historical prices
 * @return {number} Z-Score value
 * @customfunction
 * 
 * @example
 * =Z_SCORE(100; A2:A100)
 */
function Z_SCORE(currentPrice, historyRange) {
  if (typeof currentPrice !== 'number' || isNaN(currentPrice)) {
    return 0;
  }
  
  if (!historyRange || !Array.isArray(historyRange)) {
    return 0;
  }
  
  // Flatten the range and filter valid numbers
  var prices = [];
  for (var i = 0; i < historyRange.length; i++) {
    var row = historyRange[i];
    var value = Array.isArray(row) ? row[0] : row;
    
    if (typeof value === 'number' && !isNaN(value) && value > 0) {
      prices.push(value);
    }
  }
  
  if (prices.length < 2) {
    Logger.log('Z_SCORE: Dados insuficientes (mínimo 2 preços)');
    return 0;
  }
  
  try {
    // Calculate mean
    var sum = 0;
    for (var i = 0; i < prices.length; i++) {
      sum += prices[i];
    }
    var mean = sum / prices.length;
    
    // Calculate standard deviation
    var sumSquaredDiff = 0;
    for (var i = 0; i < prices.length; i++) {
      var diff = prices[i] - mean;
      sumSquaredDiff += diff * diff;
    }
    var variance = sumSquaredDiff / prices.length;
    var stdDev = Math.sqrt(variance);
    
    if (stdDev === 0) {
      Logger.log('Z_SCORE: Desvio padrão zero (preços constantes)');
      return 0;
    }
    
    // Calculate Z-Score
    var zScore = (currentPrice - mean) / stdDev;
    
    return zScore;
    
  } catch (error) {
    Logger.log('Z_SCORE: Erro no cálculo: ' + error.toString());
    return 0;
  }
}

// ============================================================================
// HELPER FUNCTIONS (NOT EXPOSED TO SHEETS)
// ============================================================================

/**
 * Test function to verify all custom functions are working.
 * Run this from Apps Script editor to check functionality.
 */
function testCustomFunctions() {
  Logger.log('=== Testing Custom Functions ===');
  
  // Test TESOURO_DIRETO
  Logger.log('Testing TESOURO_DIRETO...');
  var tesouroPrice = TESOURO_DIRETO('Tesouro IPCA+ 2035');
  Logger.log('Tesouro IPCA+ 2035 price: ' + tesouroPrice);
  
  // Test CALC_VOL
  Logger.log('Testing CALC_VOL...');
  var testPrices = [[100], [102], [101], [103], [102], [104], [103], [105]];
  var vol = CALC_VOL(testPrices);
  Logger.log('Volatility: ' + vol);
  
  // Test Z_SCORE
  Logger.log('Testing Z_SCORE...');
  var zScore = Z_SCORE(110, testPrices);
  Logger.log('Z-Score for 110: ' + zScore);
  
  Logger.log('=== Tests Complete ===');
}

/**
 * Clear the script cache (useful for debugging).
 */
function clearCache() {
  var cache = CacheService.getScriptCache();
  cache.removeAll(['tesouro_*']);
  Logger.log('Cache cleared');
}
