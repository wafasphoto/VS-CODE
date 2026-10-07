import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class MarketPrediction:
    """
    Algoritma Prediksi Harga Market menggunakan Pandas
    Menganalisis tren, moving average, dan melakukan forecasting
    """
    
    def __init__(self, symbol='STOCK', initial_price=100, volatility=0.02):
        """
        Inisialisasi dengan parameter market
        """
        self.symbol = symbol
        self.initial_price = initial_price
        self.volatility = volatility
        self.df = None
        self.predictions = None
        
    def generate_mock_data(self, days=100):
        """
        Generate mock market data dengan random walk
        """
        np.random.seed(42)
        dates = pd.date_range(start='2025-01-01', periods=days, freq='D')
        
        # Random walk untuk simulasi harga
        returns = np.random.normal(0.001, self.volatility, days)
        prices = self.initial_price * np.exp(np.cumsum(returns))
        
        # Generate volume trading
        volumes = np.random.randint(1000000, 5000000, days)
        
        # Generate additional indicators
        self.df = pd.DataFrame({
            'Date': dates,
            'Open': prices * (1 + np.random.uniform(-0.01, 0.01, days)),
            'High': prices * (1 + np.abs(np.random.normal(0.005, 0.01, days))),
            'Low': prices * (1 - np.abs(np.random.normal(0.005, 0.01, days))),
            'Close': prices,
            'Volume': volumes
        })
        
        # Pastikan High > Close > Low
        for idx in self.df.index:
            self.df.loc[idx, 'High'] = max(self.df.loc[idx, ['Close', 'High']])
            self.df.loc[idx, 'Low'] = min(self.df.loc[idx, ['Close', 'Low']])
            
        self.df = self.df.set_index('Date')
        return self.df
    
    def calculate_moving_averages(self, short_window=10, long_window=30):
        """
        Hitung Moving Average untuk identifikasi tren
        """
        self.df['MA_Short'] = self.df['Close'].rolling(window=short_window).mean()
        self.df['MA_Long'] = self.df['Close'].rolling(window=long_window).mean()
        
        # Signal: 1 jika MA_Short > MA_Long (bullish), 0 jika sebaliknya
        self.df['Signal'] = (self.df['MA_Short'] > self.df['MA_Long']).astype(int)
        
        return self.df[['Close', 'MA_Short', 'MA_Long', 'Signal']]
    
    def calculate_rsi(self, period=14):
        """
        Hitung Relative Strength Index (RSI)
        """
        delta = self.df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        self.df['RSI'] = 100 - (100 / (1 + rs))
        
        return self.df['RSI']
    
    def calculate_trend_strength(self, window=10):
        """
        Hitung kekuatan tren menggunakan slope
        """
        self.df['Daily_Return'] = self.df['Close'].pct_change()
        
        # Linear regression untuk trend
        trend_strength = []
        for i in range(len(self.df)):
            if i < window:
                trend_strength.append(np.nan)
            else:
                y = self.df['Close'].iloc[i-window:i].values
                x = np.arange(len(y))
                slope = np.polyfit(x, y, 1)[0]
                trend_strength.append(slope)
        
        self.df['Trend_Strength'] = trend_strength
        return self.df['Trend_Strength']
    
    def predict_next_prices(self, forecast_days=10):
        """
        Prediksi harga untuk hari-hari mendatang menggunakan eksponensial smoothing
        """
        # Gunakan data terakhir untuk prediksi
        last_price = self.df['Close'].iloc[-1]
        last_ma_short = self.df['MA_Short'].iloc[-1]
        last_rsi = self.df['RSI'].iloc[-1]
        avg_return = self.df['Daily_Return'].mean()
        
        forecast_dates = pd.date_range(
            start=self.df.index[-1] + timedelta(days=1),
            periods=forecast_days,
            freq='D'
        )
        
        forecast_prices = []
        forecast_confidence = []
        
        for i in range(forecast_days):
            # Prediksi berbasis exponential smoothing dan momentum
            alpha = 0.3
            predicted_price = (alpha * last_price) + ((1 - alpha) * last_ma_short)
            
            # Tambahkan trend component
            trend_component = avg_return * (i + 1)
            predicted_price = predicted_price * (1 + trend_component)
            
            # Confidence score berdasarkan RSI
            if 30 < last_rsi < 70:
                confidence = 0.85
            elif 20 < last_rsi < 80:
                confidence = 0.75
            else:
                confidence = 0.65
            
            forecast_prices.append(predicted_price)
            forecast_confidence.append(confidence)
            
            # Update untuk iterasi selanjutnya
            last_price = predicted_price
            trend_component *= 0.95  # Decay trend
        
        self.predictions = pd.DataFrame({
            'Date': forecast_dates,
            'Predicted_Price': forecast_prices,
            'Confidence': forecast_confidence
        })
        
        # Hitung upper dan lower bounds
        std_dev = self.df['Daily_Return'].std()
        self.predictions['Upper_Bound'] = self.predictions['Predicted_Price'] * (1 + 2 * std_dev)
        self.predictions['Lower_Bound'] = self.predictions['Predicted_Price'] * (1 - 2 * std_dev)
        
        return self.predictions
    
    def analyze_buy_sell_signals(self):
        """
        Generate sinyal beli/jual berdasarkan indikator
        """
        signals = []
        for i in range(len(self.df)):
            signal = 'HOLD'
            
            # Kondisi beli
            if (self.df['MA_Short'].iloc[i] > self.df['MA_Long'].iloc[i] and 
                self.df['RSI'].iloc[i] < 70):
                signal = 'BUY'
            
            # Kondisi jual
            elif (self.df['MA_Short'].iloc[i] < self.df['MA_Long'].iloc[i] and 
                  self.df['RSI'].iloc[i] > 30):
                signal = 'SELL'
            
            signals.append(signal)
        
        self.df['Signal_Action'] = signals
        return self.df[['Close', 'RSI', 'Signal_Action']]
    
    def calculate_returns_analysis(self):
        """
        Analisis return dan volatilitas
        """
        daily_return = self.df['Daily_Return'].dropna()
        
        analysis = {
            'Total_Return_%': ((self.df['Close'].iloc[-1] / self.df['Close'].iloc[0]) - 1) * 100,
            'Avg_Daily_Return_%': daily_return.mean() * 100,
            'Volatility_%': daily_return.std() * 100,
            'Max_Drawdown_%': ((self.df['Close'].min() / self.df['Close'].max()) - 1) * 100,
            'Sharpe_Ratio': (daily_return.mean() / daily_return.std()) * np.sqrt(252) if daily_return.std() != 0 else 0,
        }
        
        return pd.Series(analysis)
    
    def print_report(self):
        """
        Cetak laporan lengkap prediksi market
        """
        print("="*80)
        print(f"LAPORAN ANALISIS PREDIKSI MARKET - {self.symbol}".center(80))
        print("="*80)
        
        print("\n1. DATA HISTORIS (5 hari terakhir):")
        print(self.df[['Open', 'High', 'Low', 'Close', 'Volume']].tail(5).to_string())
        
        print("\n\n2. INDIKATOR TEKNIKAL (5 hari terakhir):")
        print(self.df[['Close', 'MA_Short', 'MA_Long', 'RSI', 'Trend_Strength']].tail(5).to_string())
        
        print("\n\n3. SINYAL BELI/JUAL (5 hari terakhir):")
        print(self.df[['Close', 'RSI', 'Signal_Action']].tail(5).to_string())
        
        print("\n\n4. ANALISIS RETURN & VOLATILITAS:")
        analysis = self.calculate_returns_analysis()
        for key, value in analysis.items():
            print(f"   {key:20s}: {value:10.2f}")
        
        print("\n\n5. PREDIKSI HARGA (10 hari mendatang):")
        print(self.predictions.to_string(index=False))
        
        print("\n\n6. RINGKASAN PREDIKSI:")
        print(f"   Harga Terakhir     : Rp {self.df['Close'].iloc[-1]:,.2f}")
        print(f"   Prediksi Rata-rata : Rp {self.predictions['Predicted_Price'].mean():,.2f}")
        print(f"   Range Prediksi     : Rp {self.predictions['Lower_Bound'].min():,.2f} - Rp {self.predictions['Upper_Bound'].max():,.2f}")
        print(f"   Confidence Rata-rata: {self.predictions['Confidence'].mean():.2%}")
        
        trend = "BULLISH ↑" if self.predictions['Predicted_Price'].mean() > self.df['Close'].iloc[-1] else "BEARISH ↓"
        print(f"   Tren Prediksi      : {trend}")
        print("\n" + "="*80)


def main():
    """
    Main function untuk menjalankan prediksi market
    """
    print("\n🚀 Inisialisasi Prediksi Market dengan Mock Data...\n")
    
    # Create instance
    predictor = MarketPrediction(symbol='PT_BANK', initial_price=5000, volatility=0.015)
    
    # Generate mock data
    print("✓ Generate data historis 100 hari...")
    predictor.generate_mock_data(days=100)
    
    # Calculate indicators
    print("✓ Hitung Moving Averages...")
    predictor.calculate_moving_averages()
    
    print("✓ Hitung RSI (Relative Strength Index)...")
    predictor.calculate_rsi()
    
    print("✓ Hitung Kekuatan Trend...")
    predictor.calculate_trend_strength()
    
    # Generate signals
    print("✓ Generate sinyal beli/jual...")
    predictor.analyze_buy_sell_signals()
    
    # Make predictions
    print("✓ Prediksi harga 10 hari mendatang...\n")
    predictor.predict_next_prices(forecast_days=10)
    
    # Print comprehensive report
    predictor.print_report()
    
    # Export results
    print("\n💾 Export hasil ke CSV...")
    predictor.df.to_csv('market_analysis.csv')
    predictor.predictions.to_csv('market_predictions.csv', index=False)
    print("✓ Berhasil export ke 'market_analysis.csv' dan 'market_predictions.csv'")


if __name__ == "__main__":
    main()
