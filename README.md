# THYAO Hisse Senedi Fiyat Tahmini Projesi

##  Proje Tanımı ve Amacı

Bu proje, **Turkish Airlines (THYAO)** hisse senedinin gelecekteki kapanış fiyatını tahmin etmek amacıyla geliştirilmiş bir makine öğrenmesi uygulamasıdır. Proje, hisse senedi verilerini analiz ederek, teknik göstergeler kullanarak ve farklı makine öğrenmesi algoritmalarını karşılaştırarak en iyi tahmin modelini bulmayı hedeflemektedir.

### Veri Seti

Bu projede kullanılan veri seti, [Borsa İstanbul Türk Hisse Senetleri Veri Seti](https://www.kaggle.com/datasets/gokhankesler/borsa-istanbul-turkish-stock-exchange-dataset) adresinden alınmıştır.


### Özellikler:
- Veri yükleme ve temizleme
- Teknik göstergeler hesaplama (günlük getiri, hareketli ortalamalar)
- Linear Regression model eğitimi
- KNN Regressor model eğitimi ve k-değeri optimizasyonu
- Model performans karşılaştırması (MSE, RMSE, MAE, R²)
- Görselleştirme ve raporlama
- Sonuçların kaydedilmesi

### Gereksinimler:
- pandas, numpy, matplotlib, seaborn, scikit-learn, scipy

### Kullanım:
    python thyao_dataset.py

### Çıktılar:
- THYAO_clean.csv: Temizlenmiş veri seti
- THYAO_train.csv: Eğitim veri seti
- THYAO_test.csv: Test veri seti
- THYAO_closing_price_trend.png
- THYAO_daily_return_distribution.png
- THYAO_knn_k_comparison.png
- THYAO_real_vs_prediction.png
- Detaylı performans raporu .(ipynb)


###  Ana Hedefler
- **Veri Analizi**: THYAO hisse senedi verilerinin detaylı analizi
- **Model Geliştirme**: Linear Regression ve KNN Regressor modellerinin eğitimi
- **Performans Karşılaştırması**: Farklı algoritmaların performans analizi
- **Tahmin**: Ertesi günün kapanış fiyatının tahmin edilmesi

###  Tahmin Edilen Değişken
- **Hedef (y)**: Ertesi günün kapanış fiyatı (Close session price)
- **Özellikler (X)**: Mevcut günün teknik göstergeleri ve fiyat verileri

##  Veri Seti ve Özellikler

###  Veri Seti Genel Bilgileri
- **Kaynak**: Borsa İstanbul (BIST) verileri
- **Zaman Aralığı**: Günlük işlem verileri
- **Sütun Sayısı**: 40+ farklı veri sütunu
- **Veri Türleri**: Fiyat, hacim, işlem sayısı, teknik göstergeler

###  Kullanılan Ana Sütunlar
**Fiyat Verileri:**
- `OPENING PRICE`: Açılış fiyatı
- `CLOSING PRICE`: Kapanış fiyatı
- `HIGHEST PRICE`: En yüksek fiyat
- `LOWEST PRICE`: En düşük fiyat

**Hacim ve İşlem Verileri:**
- `TOTAL TRADED VOLUME`: Toplam işlem hacmi
- `TOTAL TRADED VALUE`: Toplam işlem değeri
- `TOTAL NUMBER OF CONTRACTS`: Toplam kontrat sayısı

**Teknik Göstergeler:**
- `daily_return`: Günlük getiri
- `pct_change`: Yüzdelik değişim
- `moving_average_5`: 5 günlük hareketli ortalama
- `moving_average_20`: 20 günlük hareketli ortalama

##  Veri Ön İşleme ve Temizleme

###  Veri Temizleme Adımları

#### 1. **Sütun Filtreleme**
Gereksiz ve analiz için uygun olmayan sütunlar kaldırıldı:
- **Kaldırılan Sütun Sayısı**: 30+ sütun
- **Kalan Sütun Sayısı**: 10+ ana özellik

**Kaldırılan Sütun Kategorileri:**
- Piyasa bilgileri (MARKET, INSTRUMENT TYPE)
- Endeks verileri (BIST 100, BIST 30)
- Detay işlem verileri (SHORT SALE, TRADE REPORT)
- Gereksiz hesaplamalar (VWAP, REFERENCE PRICE)

#### 2. **Veri Türü Dönüşümleri**
- **Tarih sütunları**: `datetime` formatına çevrildi
- **Fiyat sütunları**: `float64` formatına çevrildi
- **Hacim sütunları**: `float64` formatına çevrildi

#### 3. **Eksik Veri İşleme**
- **Forward Fill**: Fiyat verileri için
- **Interpolate**: Hacim verileri için
- **Dropna**: Son temizlik için

#### 4. **Hatalı Veri Filtreleme**
- **Negatif fiyatlar**: -1000'den küçük değerler filtrelendi
- **Sıfır hacimler**: Geçersiz işlem verileri kaldırıldı
- **Aykırı değerler**: İstatistiksel analiz ile tespit edildi

##  Veri Temizleme Detayları

###  Silinen Sütunların Tam Listesi

**Toplam Silinen Sütun Sayısı**: 30+ sütun

**Piyasa ve Enstrüman Bilgileri:**
- `INSTRUMENT NAME`: Enstrüman adı
- `MARKET SEGMENT`: Piyasa segmenti
- `MARKET`: Piyasa bilgisi
- `INSTRUMENT TYPE`: Enstrüman türü
- `INSTRUMENT CLASS`: Enstrüman sınıfı
- `MARKET MAKER`: Piyasa yapıcısı

**Endeks Verileri:**
- `BIST 100 INDEX`: BIST 100 endeks değeri
- `BIST 30 INDEX`: BIST 30 endeks değeri

**Hesaplama ve Referans Verileri:**
- `GROSS SETTLEMENT`: Brüt takas
- `REMAINING BID`: Kalan alış emri
- `REMAINING ASK`: Kalan satış emri
- `VWAP`: Volume Weighted Average Price
- `TOTAL NUMBER OF CONTRACTS`: Toplam kontrat sayısı
- `REFERENCE PRICE`: Referans fiyatı

**Açılış Seansı Verileri:**
- `TRADED VALUE AT OPENING SESSION`: Açılış seansında işlem değeri
- `TRADED VOLUME AT OPENING SESSION`: Açılış seansında işlem hacmi
- `NUMBER OF CONTRACTS AT OPENING SESSION`: Açılış seansında kontrat sayısı

**Kapanış Seansı Verileri:**
- `TRADED VALUE AT CLOSING SESSION`: Kapanış seansında işlem değeri
- `TRADED VOLUME AT CLOSING SESSION`: Kapanış seansında işlem hacmi
- `NUMBER OF CONTRACTS AT CLOSING SESSION`: Kapanış seansında kontrat sayısı

**Kapanış Fiyatında İşlem Verileri:**
- `TRADED VALUE OF TRADES AT CLOSING PRICE`: Kapanış fiyatında işlem değeri
- `TRADED VOLUME OF TRADES AT CLOSING PRICE`: Kapanış fiyatında işlem hacmi
- `NUMBER OF CONTRACTS OF TRADES AT CLOSING PRICE`: Kapanış fiyatında kontrat sayısı

**Short Sale Verileri:**
- `LOWEST SHORT SALE PRICE`: En düşük short sale fiyatı
- `HIGHEST SHORT SALE PRICE`: En yüksek short sale fiyatı
- `SHORT SALE VWAP`: Short sale VWAP
- `TRADED VALUE OF SHORT SALE TRADES`: Short sale işlem değeri
- `TRADED VOLUME OF SHORT SALE TRADES`: Short sale işlem hacmi
- `NUMBER OF CONTRACTS OF SHORT SALE TRADES`: Short sale kontrat sayısı

**Trade Report Verileri:**
- `LOWEST TRADE REPORT PRICE`: En düşük trade report fiyatı
- `HIGHEST TRADE REPORT PRICE`: En yüksek trade report fiyatı
- `TRADE REPORT VWAP`: Trade report VWAP
- `TRADE REPORT TRADED VALUE`: Trade report işlem değeri
- `TRADE REPORT TRADED VOLUME`: Trade report işlem hacmi
- `NUMBER OF TRADE REPORTS`: Trade report sayısı

###  Teknik Göstergelerin Hesaplama Detayları

#### 1. **Günlük Getiri (daily_return)**
**Formül**: `(CLOSING_PRICE - OPENING_PRICE) / OPENING_PRICE`
- **Amaç**: Günlük fiyat değişiminin yüzdelik oranı
- **Birim**: Ondalık sayı (örn: 0.05 = %5 artış)
- **Hesaplama**: Her gün için açılış ve kapanış fiyatları kullanılarak

#### 2. **Yüzdelik Değişim (pct_change)**
**Formül**: `(CURRENT_PRICE - PREVIOUS_PRICE) / PREVIOUS_PRICE`
- **Amaç**: Bir önceki güne göre fiyat değişimi
- **Birim**: Ondalık sayı
- **Hesaplama**: Kapanış fiyatları arasında ardışık günler karşılaştırılarak

#### 3. **5 Günlük Hareketli Ortalama (moving_average_5)**
**Formül**: `(PRICE_1 + PRICE_2 + PRICE_3 + PRICE_4 + PRICE_5) / 5`
- **Amaç**: Kısa vadeli fiyat trendini yakalamak
- **Pencere**: 5 günlük kaydırılan pencere
- **Hesaplama**: Her gün için son 5 günün kapanış fiyatları ortalaması

#### 4. **20 Günlük Hareketli Ortalama (moving_average_20)**
**Formül**: `(PRICE_1 + PRICE_2 + ... + PRICE_20) / 20`
- **Amaç**: Orta vadeli fiyat trendini yakalamak
- **Pencere**: 20 günlük kaydırılan pencere
- **Hesaplama**: Her gün için son 20 günün kapanış fiyatları ortalaması

###  Veri Temizleme Süreçleri

#### 1. **Veri Türü Dönüşümleri**
- **Tarih sütunları**: `pd.to_datetime()` ile datetime formatına çevrildi
- **Fiyat sütunları**: `pd.to_numeric()` ile float64 formatına çevrildi
- **Hacim sütunları**: `pd.to_numeric()` ile float64 formatına çevrildi

#### 2. **Eksik Veri İşleme**
- **Forward Fill (ffill)**: Fiyat verileri için önceki değerle doldurma
- **Interpolate**: Hacim verileri için doğrusal interpolasyon
- **Backward Fill (bfill)**: Son değerle doldurma (gerekirse)

#### 3. **Hatalı Veri Filtreleme**
- **Negatif fiyatlar**: -1000'den küçük değerler filtrelendi
- **Sıfır hacimler**: Geçersiz işlem verileri kaldırıldı
- **Aykırı değerler**: İstatistiksel analiz ile tespit edildi

#### 4. **Veri Doğrulama**
- **Fiyat tutarlılığı**: Açılış ≤ Kapanış ≤ En yüksek kontrolü
- **Hacim tutarlılığı**: Pozitif değer kontrolü
- **Tarih tutarlılığı**: Kronolojik sıra kontrolü

#  Özellik Mühendisliği ve Hedef Değişken

###  Hedef Değişken Hazırlama
**Yarının Kapanış Fiyatı (y):**
- Mevcut günün `CLOSING PRICE` sütunu 1 gün ileri kaydırıldı (`shift(-1)`)
- Son gün için NaN değerler temizlendi
- Toplam kayıt sayısı: Eğitim + test verisi

###  Özellik Değişkenleri (X)
**Temel Fiyat Verileri:**
- `OPENING PRICE`: Günün açılış fiyatı
- `CLOSING PRICE`: Günün kapanış fiyatı
- `HIGHEST PRICE`: Günün en yüksek fiyatı
- `LOWEST PRICE`: Günün en düşük fiyatı

**Teknik Göstergeler:**
- `daily_return`: (Kapanış - Açılış) / Açılış
- `pct_change`: Bir önceki güne göre yüzdelik değişim
- `moving_average_5`: 5 günlük hareketli ortalama
- `moving_average_20`: 20 günlük hareketli ortalama

**Hacim ve İşlem Verileri:**
- `TOTAL TRADED VOLUME`: Toplam işlem hacmi
- `TOTAL TRADED VALUE`: Toplam işlem değeri
- `CHANGE TO PREVIOUS CLOSING (%)`: Önceki kapanışa göre değişim

##  Veri Seti Bölme ve Model Eğitimi

###  Train-Test Split
- **Eğitim Seti**: %80 (ilk %80 gün)
- **Test Seti**: %20 (son %20 gün)
- **Zaman Sırası**: Kronolojik sıra korundu
- **Veri Boyutu**: X=(eğitim_satırı, özellik_sayısı), y=(eğitim_satırı,)

###  Makine Öğrenmesi Modelleri

#### 1. **Linear Regression**
**Model Özellikleri:**
- Basit ve hızlı
- Doğrusal ilişkileri yakalar
- Yorumlanabilir sonuçlar

**Eğitim Süreci:**
- `LinearRegression()` modeli tanımlandı
- `.fit(X_train, y_train)` ile eğitildi
- Model parametreleri (intercept, coefficients) hesaplandı

#### 2. **K-Nearest Neighbors (KNN) Regressor**
**Model Özellikleri:**
- Parametrik olmayan model
- Lokal pattern'leri yakalar
- K değeri optimizasyonu gerekli

**K Değeri Optimizasyonu:**
- Test edilen k değerleri: [3, 5, 7, 9, 11, 15, 20]
- En iyi k değeri: R² skoruna göre seçildi
- Her k değeri için performans metrikleri hesaplandı

**Eğitim Süreci:**
- En iyi k değeri ile `KNeighborsRegressor` oluşturuldu
- Model eğitildi ve parametreler belirlendi

##  Model Performans Değerlendirmesi

###  Kullanılan Metrikler

#### 1. **Mean Squared Error (MSE)**
- Hata karelerinin ortalaması
- Düşük değer = Daha iyi performans
- Birimi: Fiyat biriminin karesi

#### 2. **Root Mean Squared Error (RMSE)**
- MSE'nin karekökü
- Düşük değer = Daha iyi performans
- Birimi: Fiyat birimi (TL)
- Yorumlanabilir hata miktarı

#### 3. **Mean Absolute Error (MAE)**
- Mutlak hataların ortalaması
- Düşük değer = Daha iyi performans
- Birimi: Fiyat birimi (TL)
- Aykırı değerlere karşı dayanıklı

#### 4. **R² Score (Coefficient of Determination)**
- Açıklanan varyans oranı
- 0-1 arası değer
- 1'e yakın = Daha iyi performans
- Modelin tahmin gücünü gösterir

###  Performans Karşılaştırması
**Her model için hesaplanan metrikler:**
- Eğitim verisi üzerinde performans
- Test verisi üzerinde performans
- Overfitting analizi (eğitim vs test farkı)
- En iyi model seçimi (R² skoruna göre)

##  Görselleştirme ve Grafikler

###  Oluşturulan Grafikler

#### 1. **Kapanış Fiyatı Trendi**
- Zaman serisi grafiği
- Fiyat değişim trendi
- Kaydedilen dosya: `THYAO_closing_price_trend.png`

#### 2. **Günlük Getiri Dağılımı**
- Histogram grafiği
- Normal dağılım analizi
- Kaydedilen dosya: `THYAO_daily_return_distribution.png`

#### 3. **Gerçek vs Tahmin Karşılaştırması**
- Scatter plot
- Her iki model için ayrı ayrı
- Kaydedilen dosya: `THYAO_actual_vs_prediction.png`

#### 4. **KNN k Değerleri Karşılaştırması**
- 2x2 subplot düzeni
- R², RMSE, MAE skorları
- En iyi k değeri işaretlendi
- Kaydedilen dosya: `THYAO_knn_k_comparison.png`

###  Grafik Kaydetme
- **Format**: PNG (yüksek çözünürlük)
- **DPI**: 300 (profesyonel kalite)
- **Konum**: Masaüstü klasörü
- **Boyut**: Otomatik optimize edilmiş

##  Sonuçlar ve Analiz

###  Model Performans Özeti

**Linear Regression:**
- Avantajlar: Hızlı, yorumlanabilir, basit
- Dezavantajlar: Doğrusal olmayan ilişkileri yakalayamaz
- Uygunluk: Basit tahminler için ideal

**KNN Regressor:**
- Avantajlar: Lokal pattern'leri yakalar, parametrik değil
- Dezavantajlar: Yavaş tahmin, bellek kullanımı yüksek
- Uygunluk: Karmaşık, doğrusal olmayan ilişkiler için

###  En İyi Model Seçimi
- **Seçim Kriteri**: Test verisi üzerinde en yüksek R² skoru
- **Karşılaştırma**: Tüm metrikler (R², RMSE, MAE) dikkate alındı
- **Sonuç**: En iyi performans gösteren model seçildi

###  Tahmin Performansı
- **R² Skoru**: Modelin açıklama gücü
- **RMSE**: Ortalama tahmin hatası (TL cinsinden)
- **MAE**: Mutlak ortalama hata (TL cinsinden)
- **Overfitting Analizi**: Eğitim vs test performans farkı

##  Gelecek İyileştirmeler ve Öneriler

###  Model İyileştirmeleri

#### 1. **Gelişmiş Algoritmalar**
- **Random Forest**: Ensemble yöntemi, daha iyi genelleme
- **XGBoost**: Gradient boosting, yüksek performans
- **LSTM**: Zaman serisi için derin öğrenme
- **SVR**: Support Vector Regression, kernel trick

#### 2. **Özellik Mühendisliği**
- **Teknik Göstergeler**: RSI, MACD, Bollinger Bands
- **Zaman Özellikleri**: Hafta günü, ay, sezon
- **Ekonomik Göstergeler**: Döviz kurları, emtia fiyatları
- **Sosyal Medya**: Sentiment analizi, haber etkisi

#### 3. **Veri Kalitesi**
- **Daha Uzun Veri**: Yıllık veri seti genişletme
- **Real-time Veri**: Canlı veri akışı
- **Alternatif Kaynaklar**: Farklı veri sağlayıcıları

###  Değerlendirme İyileştirmeleri
- **Cross-Validation**: K-fold cross validation
- **Time Series Split**: Zaman serisi için özel split
- **Hyperparameter Tuning**: Grid search, random search
- **Ensemble Methods**: Birden fazla modelin birleştirilmesi

###  Uygulama Alanları
- **Portföy Yönetimi**: Risk analizi ve optimizasyon
- **Alım-Satım Stratejileri**: Otomatik trading sinyalleri
- **Risk Yönetimi**: VaR (Value at Risk) hesaplamaları
- **Regülasyon**: Finansal kurumlar için uyumluluk

##  Proje Özeti ve Sonuçlar

###  Proje Başarısı
Bu proje, **THYAO hisse senedi fiyat tahmini** için kapsamlı bir makine öğrenmesi çözümü geliştirmeyi başarmıştır. Proje sürecinde:

 **Veri Analizi**: 40+ sütunlu veri seti analiz edildi ve temizlendi
 **Özellik Mühendisliği**: Teknik göstergeler ve fiyat verileri hazırlandı
 **Model Geliştirme**: Linear Regression ve KNN Regressor modelleri eğitildi
 **Performans Analizi**: Kapsamlı metrik hesaplamaları yapıldı
 **Görselleştirme**: 4 farklı grafik türü oluşturuldu
 **Model Karşılaştırması**: En iyi model seçildi

###  Ana Bulgular
- **Veri Kalitesi**: Yüksek kaliteli, temizlenmiş veri seti
- **Model Performansı**: Her iki model de makul tahmin gücü gösterdi
- **Teknik Göstergeler**: Hareketli ortalamalar ve getiri hesaplamaları etkili
- **Zaman Serisi**: Kronolojik veri bölme başarılı

###  Gelecek Vizyonu
Bu proje, finansal tahmin alanında daha gelişmiş modeller geliştirmek için sağlam bir temel oluşturmaktadır. Gelecekte:

- **Derin Öğrenme**: LSTM ve Transformer modelleri
- **Real-time Trading**: Canlı veri ile otomatik trading
- **Portföy Optimizasyonu**: Çoklu hisse senedi analizi
- **Risk Yönetimi**: Gelişmiş risk metrikleri

###  Öğrenilen Dersler
- **Veri Temizleme**: Finansal verilerde veri kalitesi kritik
- **Özellik Seçimi**: Doğru özellikler model performansını artırır
- **Model Karşılaştırması**: Farklı algoritmalar farklı güçlere sahip
- **Zaman Serisi**: Finansal verilerde zaman sırası önemli

---
