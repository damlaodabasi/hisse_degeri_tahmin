import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Tuple

# Matplotlib backend ayarı - grafiklerin ekranda açılması için
import matplotlib
matplotlib.use('TkAgg')  # Windows için TkAgg backend kullan
import matplotlib.pyplot as plt
import seaborn as sns

# KONFIGÜRASYON VE SABİTLER

# Dosya yolları - merkezi konfigürasyon
DESKTOP_PATH = Path(r"C:\Users\Administrator\Desktop")
INPUT_CSV_PATH = DESKTOP_PATH / "THYAO.csv"
OUTPUT_CSV_PATH = DESKTOP_PATH / "THYAO_clean.csv"

# Veri temizleme için kaldırılacak sütunlar
# Bu sütunlar analiz için gerekli olmayan veya tekrarlayan bilgiler içerir
COLUMNS_TO_REMOVE: List[str] = [
    "INSTRUMENT NAME",
    "MARKET SEGMENT",
    "MARKET",
    "INSTRUMENT TYPE",
    "INSTRUMENT CLASS",
    "MARKET MAKER",
    "BIST 100 INDEX",
    "BIST 30 INDEX",
    "GROSS SETTLEMENT",
    # "OPENING SESSION PRICE",  # Açılış fiyatı - gerekli
    # "CLOSING SESSION PRICE",  # Kapanış fiyatı - gerekli
    "REMAINING BID",
    "REMAINING ASK",
    "VWAP",
    "TOTAL NUMBER OF CONTRACTS",
    "REFERENCE PRICE",
    "TRADED VALUE AT OPENING SESSION",
    "TRADED VOLUME AT OPENING SESSION",
    "NUMBER OF CONTRACTS AT OPENING SESSION",
    "TRADED VALUE AT CLOSING SESSION",
    "TRADED VOLUME AT CLOSING SESSION",
    "NUMBER OF CONTRACTS AT CLOSING SESSION",
    "TRADED VALUE OF TRADES AT CLOSING PRICE",
    "TRADED VOLUME OF TRADES AT CLOSING PRICE",
    "NUMBER OF CONTRACTS OF TRADES AT CLOSING PRICE",
    "LOWEST SHORT SALE PRICE",
    "HIGHEST SHORT SALE PRICE",
    "SHORT SALE VWAP",
    "TRADED VALUE OF SHORT SALE TRADES",
    "TRADED VOLUME OF SHORT SALE TRADES",
    "NUMBER OF CONTRACTS OF SHORT SALE TRADES",
    "LOWEST TRADE REPORT PRICE",
    "HIGHEST TRADE REPORT PRICE",
    "TRADE REPORT VWAP",
    "TRADE REPORT TRADED VALUE",
    "TRADE REPORT TRADED VOLUME",
    "NUMBER OF TRADE REPORTS",
]


def remove_columns_from_dataframe(
    df: pd.DataFrame, columns_to_remove: List[str]
) -> Tuple[pd.DataFrame, List[str], List[str]]:
    """
    DataFrame'den belirtilen sütunları kaldırır (büyük/küçük harf duyarsız).
    
    Args:
        df: İşlenecek DataFrame
        columns_to_remove: Kaldırılacak sütun adları listesi
    
    Returns:
        Tuple[pd.DataFrame, List[str], List[str]]: 
        - Temizlenmiş DataFrame
        - Gerçekte silinen sütunların orijinal adları
        - Bulunamayan sütun adları
    """
    # Sütun adlarını normalize et (trim + uppercase) ve orijinal adlarla eşleştir
    normalized_to_original = {col.strip().upper(): col for col in df.columns}
    
    # Kaldırılacak sütunları normalize et
    requested_normalized = [name.strip().upper() for name in columns_to_remove]
    
    # Eşleşen sütunları bul
    matched_originals = [
        normalized_to_original[n]
        for n in requested_normalized
        if n in normalized_to_original
    ]
    
    # Bulunamayan sütunları tespit et
    missing_columns = [
        columns_to_remove[idx]
        for idx, n in enumerate(requested_normalized)
        if n not in normalized_to_original
    ]
    
    # Eşleşen sütunları DataFrame'den kaldır
    new_df = df.drop(columns=matched_originals, errors="ignore")
    return new_df, matched_originals, missing_columns


def main() -> None:
    """
    THYAO hisse senedi veri analizi ve makine öğrenmesi ana fonksiyonu.
    
    Bu fonksiyon şu adımları gerçekleştirir:
    1. CSV veri dosyasını yükle
    2. Tarih sütununu işle ve sırala
    3. Veri temizleme ve filtreleme
    4. Teknik göstergeler hesapla
    5. Model eğitimi ve değerlendirme
    6. Sonuçları görselleştir ve kaydet
    """
    # 1. VERİ YÜKLEME
    
    # CSV dosyasını yükle
    try:
        df = pd.read_csv(INPUT_CSV_PATH, encoding="utf-8-sig")
        print(f"Veri yüklendi: {len(df)} kayıt, {len(df.columns)} sütun")
    except FileNotFoundError:
        print(f"Dosya bulunamadı: {INPUT_CSV_PATH}")
        return
    except Exception as e:
        print(f"CSV yüklenirken hata oluştu: {e}")
        return

    # 2. TARİH SÜTUNU İŞLEME
    
    # TRADE DATE sütununu bul ve datetime tipine çevir
    try:
        # TRADE DATE sütununu bul (büyük/küçük harf duyarsız)
        trade_date_col = None
        for col in df.columns:
            if col.strip().upper() == "TRADE DATE":
                trade_date_col = col
                break
        
        if trade_date_col is None:
            print("TRADE DATE sütunu bulunamadı!")
            return
        
        # Datetime tipine çevir ve tarihe göre sırala
        df[trade_date_col] = pd.to_datetime(df[trade_date_col], errors='coerce')
        df = df.sort_values(by=trade_date_col)
        
        # Tekrarlanan tarihleri kaldır (ilk kaydı tut)
        df = df.drop_duplicates(subset=[trade_date_col], keep='first')
        
        print(f"Tarih sütunu işlendi ve sıralandı")
        print(f"Tekrarlanan tarihler kaldırıldı. Toplam kayıt sayısı: {len(df)}")
        
    except Exception as e:
        print(f"Tarih sütunu işlenirken hata oluştu: {e}")
        return

    # 3. ASKIYA ALINAN İŞLEMLERİ FİLTRELEME
    
    # SUSPENDED=1 olan satırları kaldır (askıya alınan işlemler)
    try:
        # SUSPENDED sütununu bul (büyük/küçük harf duyarsız)
        suspended_col = None
        for col in df.columns:
            if col.strip().upper() == "SUSPENDED":
                suspended_col = col
                break
        
        if suspended_col is not None:
            # Askıya alınan işlemleri filtrele
            initial_count = len(df)
            df = df[df[suspended_col] != 1]
            removed_count = initial_count - len(df)
            
            if removed_count > 0:
                print(f"Askıya alınan işlemler (SUSPENDED=1) kaldırıldı: {removed_count} satır")
            else:
                print("Askıya alınan işlem bulunamadı")
            
            print(f"Filtreleme sonrası kalan kayıt sayısı: {len(df)}")
        else:
            print("SUSPENDED sütunu bulunamadı, filtreleme yapılamadı")
            
    except Exception as e:
        print(f"SUSPENDED sütunu işlenirken hata oluştu: {e}")
        return

    # 4. SAYISAL SÜTUNLARI TEMİZLEME VE DÖNÜŞTÜRME
    
    # Sayısal sütunları tespit et ve float tipine çevir
    try:
        # Sayısal sütunları tanımla (fiyat, hacim, değişim yüzdesi vb.)
        numeric_keywords = [
            'PRICE', 'VOLUME', 'VALUE', 'CHANGE', 'PERCENT', 'RATIO', 'AMOUNT',
            'QUANTITY', 'NUMBER', 'COUNT', 'RATE', 'INDEX', 'BID', 'ASK',
            'OPEN', 'CLOSE', 'HIGH', 'LOW', 'AVERAGE', 'MEAN', 'TOTAL'
        ]
        
        # Sayısal anahtar kelimeleri içeren sütunları bul
        numeric_columns = []
        for col in df.columns:
            col_upper = col.strip().upper()
            if any(keyword in col_upper for keyword in numeric_keywords):
                numeric_columns.append(col)
        
        print(f"Sayısal sütunlar tespit edildi: {len(numeric_columns)} adet")
        
        # Her sayısal sütunu temizle ve float'a çevir
        for col in numeric_columns:
            try:
                # Veriyi string'e çevir
                df[col] = df[col].astype(str)
                
                # Veri temizleme işlemleri:
                # - Virgülleri kaldır (binlik ayraç)
                # - Boşlukları kaldır
                # - Türkçe tire karakterlerini standart tire ile değiştir
                df[col] = df[col].str.replace(',', '', regex=False)  # Binlik ayraç
                df[col] = df[col].str.replace(' ', '', regex=False)  # Boşluklar
                df[col] = df[col].str.replace('−', '-', regex=False)  # Türkçe tire
                df[col] = df[col].str.replace('–', '-', regex=False)  # Farklı tire karakteri
                
                # Yüzde işaretini kaldır
                df[col] = df[col].str.replace('%', '', regex=False)
                
                # Float tipine çevir
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
            except Exception as e:
                print(f"  [HATA] {col}: Hata - {e}")
                continue
        
        print("Sayısal sütunlar float tipine çevrildi ve temizlendi")
        
    except Exception as e:
        print(f"Sayısal sütunlar işlenirken hata oluştu: {e}")
        return

    # 5. VERİ DOĞRULAMA VE TEMİZLEME
    
    # Eksik değerleri işle ve hatalı değerleri filtrele
    try:
        # Kritik sayısal sütunlar için doğrulama kuralları
        critical_columns = {
            'PRICE': {'min_value': 0, 'allow_zero': False, 'fill_method': 'forward'},
            'VOLUME': {'min_value': 0, 'allow_zero': False, 'fill_method': 'interpolate'},
            'VALUE': {'min_value': 0, 'allow_zero': False, 'fill_method': 'interpolate'},
            'CHANGE': {'min_value': None, 'allow_zero': True, 'fill_method': 'forward'},
            'PERCENT': {'min_value': None, 'allow_zero': True, 'fill_method': 'forward'},
            'OPEN': {'min_value': 0, 'allow_zero': False, 'fill_method': 'forward'},
            'CLOSE': {'min_value': 0, 'allow_zero': False, 'fill_method': 'forward'},
            'HIGH': {'min_value': 0, 'allow_zero': False, 'fill_method': 'forward'},
            'LOW': {'min_value': 0, 'allow_zero': False, 'fill_method': 'forward'}
        }
        
        initial_count = len(df)
        removed_rows = 0
        
        # Her kritik sütunu kontrol et ve doğrula
        for col_pattern, rules in critical_columns.items():
            matching_cols = [col for col in df.columns if col_pattern in col.strip().upper()]
            
            for col in matching_cols:
                try:
                    # Eksik değerleri tespit et ve doldur
                    missing_count = df[col].isna().sum()
                    
                    if missing_count > 0:
                        # Eksik değerleri doldur (forward fill veya interpolate)
                        if rules['fill_method'] == 'forward':
                            df[col] = df[col].fillna(method='ffill').fillna(method='bfill')
                        elif rules['fill_method'] == 'interpolate':
                            df[col] = df[col].interpolate(method='linear').fillna(method='ffill').fillna(method='bfill')
                    
                    # Hatalı değerleri filtrele
                    if rules['min_value'] is not None:
                        if rules['allow_zero']:
                            # Sıfır dahil minimum değer kontrolü
                            invalid_mask = df[col] < rules['min_value']
                        else:
                            # Sıfır hariç minimum değer kontrolü
                            if 'PRICE' in col.upper():
                                # Fiyat sütunları için sadece çok negatif değerleri filtrele
                                invalid_mask = (df[col] < -1000) | (df[col].isna())
                            else:
                                # Diğer sütunlar için normal filtreleme
                                invalid_mask = (df[col] <= rules['min_value']) | (df[col].isna())
                        
                        invalid_count = invalid_mask.sum()
                        
                        if invalid_count > 0:
                            df = df[~invalid_mask]
                            removed_rows += invalid_count
                    
                except Exception as e:
                    print(f"  ✗ {col}: Hata - {e}")
                    continue
        
        # Veri temizleme özeti
        final_count = len(df)
        total_removed = initial_count - final_count
        
        if total_removed > 0:
            print(f"\nVeri temizleme tamamlandı:")
            print(f"  Başlangıç kayıt sayısı: {initial_count}")
            print(f"  Kaldırılan kayıt sayısı: {total_removed}")
            print(f"  Kalan kayıt sayısı: {final_count}")
        else:
            print(f"\nTüm veriler geçerli, hiçbir kayıt kaldırılmadı")
        
    except Exception as e:
        print(f"Veri doğrulama ve temizleme sırasında hata oluştu: {e}")
        return

    # YORUM: Teknik göstergeleri hesapla ve yeni sütunlar olarak ekle
    try:
        # Gerekli sütunları bul
        closing_price_col = None
        opening_price_col = None
        
        # Kapanış fiyatı için olası sütun isimleri
        possible_close_names = ['CLOSING PRICE', 'CLOSING SESSION PRICE', 'CLOSE', 'CLOSING', 'CLOSE PRICE', 'LAST', 'LAST PRICE', 'SETTLEMENT', 'SETTLEMENT PRICE']
        possible_open_names = ['OPENING PRICE', 'OPENING SESSION PRICE', 'OPEN', 'OPENING', 'OPEN PRICE', 'FIRST', 'FIRST PRICE']
        
        # Her sütunu kontrol et
        for col in df.columns:
            col_upper = col.strip().upper()
            
            # Kapanış fiyatı sütununu bul
            if col_upper == 'CLOSING PRICE':
                closing_price_col = col
                break
            elif col_upper == 'CLOSING SESSION PRICE':
                closing_price_col = col
                break
            elif any(close_name in col_upper for close_name in possible_close_names):
                if 'SETTLEMENT' not in col_upper or 'CLOSING' in col_upper:
                    closing_price_col = col
                    break
            
            # Açılış fiyatı sütununu bul
            if col_upper == 'OPENING PRICE':
                opening_price_col = col
            elif col_upper == 'OPENING SESSION PRICE':
                opening_price_col = col
            elif any(open_name in col_upper for open_name in possible_open_names):
                opening_price_col = col
        
        # Eğer bulunamazsa, hata ver
        if closing_price_col is None:
            print(f"Kapanış fiyatı sütunu bulunamadı!")
            return
        
        if opening_price_col is None:
            print(f"Açılış fiyatı sütunu bulunamadı, daily_return hesaplanamayacak!")
            opening_price_col = closing_price_col  # Geçici olarak kapanış fiyatını kullan
            print(f"  [UYARI] Açılış fiyatı bulunamadı, kapanış fiyatı kullanılarak devam ediliyor")
        
        print(f"  Kullanılan sütunlar: '{opening_price_col}', '{closing_price_col}'")
        
        # 1. Daily Return: (closing_price - opening_price) / opening_price
        if opening_price_col != closing_price_col:
            # Normal durum: açılış ve kapanış fiyatları farklı
            df['daily_return'] = (df[closing_price_col] - df[opening_price_col]) / df[opening_price_col]
            print(f"  [OK] daily_return sütunu eklendi (açılış ve kapanış fiyatlarından)")
        else:
            # Açılış fiyatı bulunamadı: alternatif hesaplama
            print(f"  [UYARI] Açılış fiyatı bulunamadı, daily_return alternatif yöntemle hesaplanıyor...")
            
            # Alternatif 1: Önceki günün kapanış fiyatından hesapla
            try:
                df['daily_return'] = df[closing_price_col].pct_change()
                print(f"  [OK] daily_return sütunu eklendi (önceki günün kapanış fiyatından)")
            except Exception as e:
                print(f"  [HATA] daily_return hesaplanamadı: {e}")
                # Boş sütun oluştur
                df['daily_return'] = np.nan
        
        # 2. Percentage Change: closing_price.pct_change() (önceki güne göre yüzdesel değişim)
        try:
            df['pct_change'] = df[closing_price_col].pct_change()
            print(f"  [OK] pct_change sütunu eklendi")
        except Exception as e:
            print(f"  [HATA] pct_change hesaplanamadı: {e}")
            df['pct_change'] = np.nan
        
        # 3. Moving Average 5: closing_price.rolling(window=5).mean()
        try:
            df['moving_average_5'] = df[closing_price_col].rolling(window=5, min_periods=1).mean()
            print(f"  [OK] moving_average_5 sütunu eklendi")
        except Exception as e:
            print(f"  [HATA] moving_average_5 hesaplanamadı: {e}")
            df['moving_average_5'] = np.nan
        
        # 4. Moving Average 20: closing_price.rolling(window=20).mean()
        try:
            df['moving_average_20'] = df[closing_price_col].rolling(window=20, min_periods=1).mean()
            print(f"  [OK] moving_average_20 sütunu eklendi")
        except Exception as e:
            print(f"  [HATA] moving_average_20 hesaplanamadı: {e}")
            df['moving_average_20'] = np.nan
        
        # Yeni sütunların istatistiklerini göster
        print(f"\nTeknik göstergeler hesaplandı:")
        print(f"  daily_return: Ortalama {df['daily_return'].mean():.4f}, Std {df['daily_return'].std():.4f}")
        print(f"  pct_change: Ortalama {df['pct_change'].mean():.4f}, Std {df['pct_change'].std():.4f}")
        print(f"  moving_average_5: Ortalama {df['moving_average_5'].mean():.2f}")
        print(f"  moving_average_20: Ortalama {df['moving_average_20'].mean():.2f}")
        
        # NaN değerleri temizle (ilk günler için)
        initial_nan_count = df.isna().sum().sum()
        df = df.dropna()
        final_nan_count = df.isna().sum().sum()
        
        if initial_nan_count > final_nan_count:
            print(f"  NaN değerler temizlendi: {initial_nan_count - final_nan_count} adet")
        
        print(f"  Toplam kayıt sayısı: {len(df)}")
        
    except Exception as e:
        print(f"Teknik göstergeler hesaplanırken hata oluştu: {e}")
        return

    # 7. EKSİK VERİ ANALİZİ VE TEMİZLEME
    
    # NaN değerleri tespit et ve uygun yöntemlerle doldur
    try:
        print(f"\nEksik veri analizi ve temizleme...")
        
        # NaN değerleri tespit et
        nan_summary = df.isna().sum()
        total_nan = nan_summary.sum()
        
        if total_nan > 0:
            print(f"  Toplam NaN değer sayısı: {total_nan}")
            print(f"  NaN içeren sütunlar:")
            for col, nan_count in nan_summary.items():
                if nan_count > 0:
                    percentage = (nan_count / len(df)) * 100
                    print(f"    {col}: {nan_count} ({percentage:.2f}%)")
            
            # NaN değerleri doldur veya satır sil
            print(f"\n  NaN değerler işleniyor...")
            
            # Sayısal sütunlarda NaN değerleri doldur
            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
            for col in numeric_cols:
                if df[col].isna().sum() > 0:
                    # Hareketli ortalama gibi sütunlarda forward fill kullan
                    if 'moving_average' in col.lower():
                        df[col] = df[col].fillna(method='ffill').fillna(method='bfill')
                        print(f"    [OK] {col}: Forward/backward fill ile dolduruldu")
                    else:
                        # Diğer sayısal sütunlarda interpolate kullan
                        df[col] = df[col].interpolate(method='linear').fillna(method='ffill').fillna(method='bfill')
                        print(f"    [OK] {col}: Interpolate ile dolduruldu")
            
            # Kategorik sütunlarda NaN değerleri doldur
            categorical_cols = df.select_dtypes(include=['object']).columns
            for col in categorical_cols:
                if df[col].isna().sum() > 0:
                    df[col] = df[col].fillna('Unknown')
                    print(f"    [OK] {col}: 'Unknown' ile dolduruldu")
            
            # Kalan NaN değerleri olan satırları sil
            remaining_nan = df.isna().sum().sum()
            if remaining_nan > 0:
                initial_rows = len(df)
                df = df.dropna()
                removed_rows = initial_rows - len(df)
                print(f"    [UYARI] {removed_rows} satır NaN değerler nedeniyle silindi")
        else:
            print(f"  [OK] Hiç NaN değer bulunamadı")
        
        print(f"  Temizleme sonrası kayıt sayısı: {len(df)}")
        
    except Exception as e:
        print(f"NaN değer temizleme sırasında hata oluştu: {e}")
        return

    # Veri türlerini düzenleme
    try:
        # Tarih sütununu datetime formatına çevir
        for col in df.columns:
            if 'DATE' in col.upper() or 'TIME' in col.upper():
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Fiyat ve hacim sütunlarını float formatına çevir
        price_volume_keywords = ['PRICE', 'VOLUME', 'VALUE', 'AMOUNT', 'QUANTITY', 'RETURN', 'CHANGE', 'PERCENT']
        for col in df.columns:
            col_upper = col.upper()
            if any(keyword in col_upper for keyword in price_volume_keywords):
                if df[col].dtype != 'float64':
                    df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Teknik göstergeleri float formatına çevir
        technical_cols = ['daily_return', 'pct_change', 'moving_average_5', 'moving_average_20']
        for col in technical_cols:
            if col in df.columns:
                df[col] = df[col].astype('float64')
        
        print(f"Veri türleri düzenlendi")
        
    except Exception as e:
        print(f"Veri türleri düzenlenirken hata oluştu: {e}")
        return

    # Özellik ve hedef değişkenleri ayırma (X, y)
    try:
        # Hedef değişkeni bul (closing_price)
        target_col = None
        possible_target_names = [
            'CLOSING PRICE', 'CLOSING SESSION PRICE', 'CLOSE', 'CLOSING', 'CLOSE PRICE', 'LAST', 'LAST PRICE', 'SETTLEMENT', 'SETTLEMENT PRICE'
        ]
        
        # Her sütunu kontrol et - CLOSING PRICE öncelikli
        for col in df.columns:
            col_upper = col.strip().upper()
            
            # Kapanış fiyatı sütununu bul - tam eşleşme öncelikli
            if col_upper == 'CLOSING PRICE':
                target_col = col
                break
            elif col_upper == 'CLOSING SESSION PRICE':
                target_col = col
                break
            elif any(close_name in col_upper for close_name in possible_target_names):
                # GROSS SETTLEMENT gibi yanlış sütunları filtrele
                if 'SETTLEMENT' not in col_upper or 'CLOSING' in col_upper:
                    target_col = col
                    break
        
        if target_col is None:
            print(f"Hedef değişken bulunamadı!")
            return
        
        # Hedef değişkeni ayır (y) - yarının kapanış fiyatı
        y = df[target_col].shift(-1).copy()  # shift(-1) ile yarının değeri
        
        # Son günün NaN değerini kaldır (yarın olmadığı için)
        y = y.dropna()
        df_aligned = df.iloc[:-1].copy()  # Son gün hariç tüm veri
        
        print(f"  [OK] Hedef değişken: yarının {target_col}")
        print(f"  [OK] Hedef değişken boyutu: {len(y)}")
        
        # Özellik değişkenleri ayır (X) - bugünün verileri
        print(f"  Özellik değişkenleri hazırlanıyor: bugünün verileri...")
        
        # Özellik olarak kullanılacak sütunları seç
        feature_columns = [
            # Fiyat verileri
            'OPENING PRICE', 'OPENING SESSION PRICE', 'LOWEST PRICE', 'HIGHEST PRICE', 
            'CLOSING PRICE', 'CLOSING SESSION PRICE', 'REFERENCE PRICE',
            
            # Hacim ve değer verileri
            'TOTAL TRADED VOLUME', 'TOTAL TRADED VALUE',
            'TRADED VOLUME AT OPENING SESSION', 'TRADED VALUE AT OPENING SESSION',
            'TRADED VOLUME AT CLOSING SESSION', 'TRADED VALUE AT CLOSING SESSION',
            'TRADED VOLUME OF TRADES AT CLOSING PRICE', 'TRADED VALUE OF TRADES AT CLOSING PRICE',
            
            # Teknik göstergeler
            'daily_return', 'pct_change', 'moving_average_5', 'moving_average_20',
            
            # Diğer önemli veriler
            'CHANGE TO PREVIOUS CLOSING (%)', 'VWAP', 'TOTAL NUMBER OF CONTRACTS',
            'REMAINING BID', 'REMAINING ASK'
        ]
        
        # Mevcut sütunlardan özellik sütunlarını bul
        available_features = []
        for feature in feature_columns:
            for col in df.columns:
                if col.upper() == feature.upper():
                    available_features.append(col)
                    break
        
        # Özellik verilerini hazırla (X)
        X = df_aligned[available_features].copy()
        
        # NaN değerleri temizle
        initial_rows = len(X)
        X = X.dropna()
        y = y.iloc[:len(X)]  # X ile aynı boyutta yap
        
        print(f"Özellik değişkenleri: {len(available_features)} adet")
        print(f"Veri boyutu: X={X.shape}, y={y.shape}")
        
    except Exception as e:
        print(f"Özellik/hedef ayrımı sırasında hata oluştu: {e}")
        return

    # 1. VERİ SETİNİ AYIRMA
    try:
        print(f"\n1. VERİ SETİNİ AYIRMA")
        
        print(f"X → Teknik göstergeler ve özellikler ({len(available_features)} adet)")
        print(f"y → Close session price (kapanış fiyatı)")
        print(f"Veri boyutu: X={X.shape}, y={y.shape}")
        
        # train_test_split ile veriyi %80 eğitim, %20 test olarak ayır
        train_size = int(len(df) * 0.8)  # %80 eğitim
        
        # Eğitim seti (ilk %80)
        X_train = X.iloc[:train_size]
        y_train = y.iloc[:train_size]
        
        # Test seti (son %20)
        X_test = X.iloc[train_size:]
        y_test = y.iloc[train_size:]
        
        print(f"\n  [OK] Veri seti ayrıldı:")
        print(f"    Eğitim seti: {X_train.shape[0]} kayıt (%80)")
        print(f"    Test seti: {X_test.shape[0]} kayıt (%20)")
        print(f"    Toplam: {len(df)} kayıt")
        
        # Eğitim ve test setlerini DataFrame olarak kaydet
        train_df = pd.concat([X_train, y_train], axis=1)
        test_df = pd.concat([X_test, y_test], axis=1)
        
        # Dosya yollarını tanımla
        train_output_path = DESKTOP_PATH / "THYAO_train.csv"
        test_output_path = DESKTOP_PATH / "THYAO_test.csv"
        
        # Eğitim ve test setlerini kaydet
        train_df.to_csv(train_output_path, index=False, encoding="utf-8-sig")
        test_df.to_csv(test_output_path, index=False, encoding="utf-8-sig")
        
        print(f"  [OK] Veri setleri kaydedildi:")
        print(f"    Eğitim: {train_output_path}")
        print(f"    Test: {test_output_path}")
        
    except Exception as e:
        print(f"Veri bölme sırasında hata oluştu: {e}")
        return

            # 8. LINEAR REGRESSION MODEL EĞİTİMİ
    
    # Linear Regression modelini eğit ve değerlendir
    try:
        print(f"\n2. LINEAR REGRESSION EĞİTME")
        
        # Gerekli kütüphaneleri import et
        from sklearn.linear_model import LinearRegression
        from sklearn.neighbors import KNeighborsRegressor
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        import numpy as np
        
        # Linear Regression modelini tanımla ve eğit
        lr_model = LinearRegression()
        lr_model.fit(X_train, y_train)
        
        # Eğitim ve test verileri üzerinde tahmin yap
        lr_train_pred = lr_model.predict(X_train)
        lr_test_pred = lr_model.predict(X_test)
        
        # 3. TAHMİN VE DEĞERLENDİRME
        print(f"\n3. TAHMİN VE DEĞERLENDİRME")
        
        print(f"mean_squared_error, mean_absolute_error, r2_score ile performans ölçülüyor...")
        
        # Linear Regression performans metrikleri
        lr_train_mse = mean_squared_error(y_train, lr_train_pred)
        lr_test_mse = mean_squared_error(y_test, lr_test_pred)
        lr_train_rmse = np.sqrt(lr_train_mse)
        lr_test_rmse = np.sqrt(lr_test_mse)
        lr_train_mae = mean_absolute_error(y_train, lr_train_pred)
        lr_test_mae = mean_absolute_error(y_test, lr_test_pred)
        lr_train_r2 = r2_score(y_train, lr_train_pred)
        lr_test_r2 = r2_score(y_test, lr_test_pred)
        
        print(f"\n  Linear Regression Performans Metrikleri:")
        print(f"    Eğitim verisi:")
        print(f"      MSE: {lr_train_mse:.6f}")
        print(f"      RMSE: {lr_train_rmse:.6f}")
        print(f"      MAE: {lr_train_mae:.6f}")
        print(f"      R²: {lr_train_r2:.6f}")
        print(f"    Test verisi:")
        print(f"      MSE: {lr_test_mse:.6f}")
        print(f"      RMSE: {lr_test_rmse:.6f}")
        print(f"      MAE: {lr_test_mae:.6f}")
        print(f"      R²: {lr_test_r2:.6f}")
        
        # 4. SONUÇLARI KAYDETME
        print(f"\n4. SONUÇLARI KAYDETME")
        
        # Linear Regression sonuçlarını sakla (KNN ile karşılaştırmak için)
        lr_results = {
            'model': 'Linear Regression',
            'train_mse': lr_train_mse,
            'test_mse': lr_test_mse,
            'train_rmse': lr_train_rmse,
            'test_rmse': lr_test_rmse,
            'train_mae': lr_train_mae,
            'test_mae': lr_test_mae,
            'train_r2': lr_train_r2,
            'test_r2': lr_test_r2
        }
        
        print(f"  Linear Regression sonuçları kaydedildi:")
        print(f"    MSE: {lr_results['test_mse']:.6f}")
        print(f"    RMSE: {lr_results['test_rmse']:.6f}")
        print(f"    MAE: {lr_results['test_mae']:.6f}")
        print(f"    R²: {lr_results['test_r2']:.6f}")
        
        # 9. KNN REGRESSOR MODEL EĞİTİMİ VE OPTİMİZASYONU
        
        # Farklı k değerlerini test ederek en iyi KNN modelini bul
        print(f"\nKNN REGRESSOR EĞİTİMİ VE OPTİMİZASYONU")
        
        # K değerlerini test et ve en iyi sonucu bul
        print(f"Farklı k değerleri deneniyor (n_neighbors)...")
        k_values = [3, 5, 7, 9, 11, 15, 20]
        knn_results_list = []
        
        best_k = 5
        best_knn_r2 = -float('inf')
        
        for k in k_values:
            print(f"  k={k} deneniyor...")
            
            # KNN modeli oluştur ve eğit
            knn_temp = KNeighborsRegressor(n_neighbors=k)
            knn_temp.fit(X_train, y_train)
            
            # Test verisi üzerinde tahmin yap
            knn_temp_pred = knn_temp.predict(X_test)
            
            # Performans metriklerini hesapla
            knn_temp_r2 = r2_score(y_test, knn_temp_pred)
            knn_temp_mse = mean_squared_error(y_test, knn_temp_pred)
            knn_temp_rmse = np.sqrt(knn_temp_mse)
            knn_temp_mae = mean_absolute_error(y_test, knn_temp_pred)
            
            # Sonuçları sakla
            knn_results_list.append({
                'k': k,
                'r2': knn_temp_r2,
                'mse': knn_temp_mse,
                'rmse': knn_temp_rmse,
                'mae': knn_temp_mae
            })
            
            print(f"    k={k}: R²={knn_temp_r2:.4f}, RMSE={knn_temp_rmse:.4f}, MAE={knn_temp_mae:.4f}")
            
            # En iyi k değerini güncelle
            if knn_temp_r2 > best_knn_r2:
                best_knn_r2 = knn_temp_r2
                best_k = k
        
        print(f"\n  [EN IYI] En iyi k değeri: {best_k} (R²: {best_knn_r2:.4f})")
        
        # En iyi k değeri ile final KNN modeli oluştur
        knn_model = KNeighborsRegressor(n_neighbors=best_k)
        knn_model.fit(X_train, y_train)
        
        # KNN tahminleri
        knn_train_pred = knn_model.predict(X_train)
        knn_test_pred = knn_model.predict(X_test)
        
        # KNN performans metrikleri
        print(f"\nmean_squared_error, mean_absolute_error, r2_score ile performans ölçülüyor...")
        
        knn_train_mse = mean_squared_error(y_train, knn_train_pred)
        knn_test_mse = mean_squared_error(y_test, knn_test_pred)
        knn_train_rmse = np.sqrt(knn_train_mse)
        knn_test_rmse = np.sqrt(knn_test_mse)
        knn_train_mae = mean_absolute_error(y_train, knn_train_pred)
        knn_test_mae = mean_absolute_error(y_test, knn_test_pred)
        knn_train_r2 = r2_score(y_train, knn_train_pred)
        knn_test_r2 = r2_score(y_test, knn_test_pred)
        
        print(f"\n  KNN Regressor Performans Metrikleri:")
        print(f"    Eğitim verisi:")
        print(f"      MSE: {knn_train_mse:.6f}")
        print(f"      RMSE: {knn_train_rmse:.6f}")
        print(f"      MAE: {knn_train_mae:.6f}")
        print(f"      R²: {knn_train_r2:.6f}")
        print(f"    Test verisi:")
        print(f"      MSE: {knn_test_mse:.6f}")
        print(f"      RMSE: {knn_test_rmse:.6f}")
        print(f"      MAE: {knn_test_mae:.6f}")
        print(f"      R²: {knn_test_r2:.6f}")
        
        # KNN sonuçlarını sakla
        knn_results = {
            'model': f'KNN Regressor (k={best_k})',
            'train_mse': knn_train_mse,
            'test_mse': knn_test_mse,
            'train_rmse': knn_train_rmse,
            'test_rmse': knn_test_rmse,
            'train_mae': knn_train_mae,
            'test_mae': knn_test_mae,
            'train_r2': knn_train_r2,
            'test_r2': knn_test_r2,
            'best_k': best_k,
            'knn_results_list': knn_results_list
        }
        
        print(f"\n  KNN Regressor sonuçları kaydedildi:")
        print(f"    En iyi k: {best_k}")
        print(f"    MSE: {knn_results['test_mse']:.6f}")
        print(f"    RMSE: {knn_results['test_rmse']:.6f}")
        print(f"    MAE: {knn_results['test_mae']:.6f}")
        print(f"    R²: {knn_results['test_r2']:.6f}")
        
        # K değerleri karşılaştırması
        print(f"\n  K değerleri karşılaştırması:")
        print(f"    {'k':<5} {'R²':<10} {'RMSE':<10} {'MAE':<10}")
        print(f"    {'-'*35}")
        for result in knn_results_list:
            print(f"    {result['k']:<5} {result['r2']:<10.4f} {result['rmse']:<10.4f} {result['mae']:<10.4f}")
        
        # MODEL KARŞILAŞTIRMASI VE SONUÇLAR
        print(f"\nMODEL KARŞILAŞTIRMASI VE SONUÇLAR")
        
        # Tüm sonuçları bir araya getir
        all_results = [lr_results, knn_results]
        
        print(f"  Model Karşılaştırması:")
        print(f"    {'Model':<20} {'R²':<10} {'RMSE':<10} {'MAE':<10}")
        print(f"    {'-'*50}")
        
        for result in all_results:
            print(f"    {result['model']:<20} {result['test_r2']:<10.4f} {result['test_rmse']:<10.4f} {result['test_mae']:<10.4f}")
        
        # En iyi modeli belirle
        best_result = max(all_results, key=lambda x: x['test_r2'])
        print(f"\n  [EN IYI] En iyi model: {best_result['model']}")
        print(f"    R²: {best_result['test_r2']:.6f}")
        print(f"    RMSE: {best_result['test_rmse']:.6f}")
        print(f"    MAE: {best_result['test_mae']:.6f}")
        

        
        # Sonuçları dosyaya kaydet
        results_summary = {
            'best_model': best_result['model'],
            'best_r2': best_result['test_r2'],
            'best_rmse': best_result['test_rmse'],
            'best_mae': best_result['test_mae'],
            'all_results': all_results
        }
        

        
        # 11. YORUMLAMA VE RAPORLAMA
        
        # Model performanslarını analiz et ve detaylı rapor oluştur
        print(f"\n5. YORUMLAMA VE RAPORLAMA")
        
        # Model performans analizi tablosu
        print(f"\n  MODEL PERFORMANS ANALİZİ:")
        print(f"    {'Model':<25} {'R²':<10} {'RMSE':<10} {'MAE':<10} {'Durum':<15}")
        print(f"    {'-'*70}")
        
        for result in all_results:
            # Performans durumunu belirle (R² skoruna göre)
            if result['test_r2'] > 0.7:
                status = "MÜKEMMEL"
            elif result['test_r2'] > 0.5:
                status = "İYİ"
            elif result['test_r2'] > 0.3:
                status = "ORTA"
            else:
                status = "DÜŞÜK"
            
            print(f"    {result['model']:<25} {result['test_r2']:<10.4f} {result['test_rmse']:<10.4f} {result['test_mae']:<10.4f} {status:<15}")
        
        # En iyi model detaylı analizi
        print(f"\n  EN İYİ MODEL ANALİZİ:")
        print(f"    Model: {best_result['model']}")
        print(f"    R² Skoru: {best_result['test_r2']:.4f}")
        print(f"    RMSE: {best_result['test_rmse']:.4f}")
        print(f"    MAE: {best_result['test_mae']:.4f}")
        

        
    except ImportError as e:
        print(f"  [UYARI] Gerekli kütüphaneler bulunamadı: {e}")
        print(f"    Model eğitimi yapılamadı. scikit-learn kurulumu gerekli.")
    except Exception as e:
        print(f"  ✗ Model eğitimi sırasında hata: {e}")
        print(f"    Model eğitimi yapılamadı.")

    # YORUM: Grafikleri oluştur ve kaydet
    try:
        print(f"\nGrafikler oluşturuluyor...")
        
        # Türkçe karakter desteği için font ayarı
        plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'SimHei']
        
        # Grafik stilini ayarla
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # 10. GÖRSELLEŞTİRME VE GRAFİK OLUŞTURMA
        
        # 1. Kapanış fiyatı trendi (zaman serisi grafiği)
        print(f"  Kapanış fiyatı trendi çiziliyor...")
        
        plt.figure(figsize=(14, 8))
        
        # Ana trend çizgisi - kapanış fiyatları
        plt.plot(df.index, df[target_col], linewidth=2, color='#2E86AB', alpha=0.8, label='Kapanış Fiyatı')
        
        # Hareketli ortalamalar - trend analizi için
        if 'moving_average_5' in df.columns:
            plt.plot(df.index, df['moving_average_5'], linewidth=1.5, color='#A23B72', alpha=0.7, label='5 Günlük Hareketli Ortalama')
        
        if 'moving_average_20' in df.columns:
            plt.plot(df.index, df['moving_average_20'], linewidth=1.5, color='#F18F01', alpha=0.7, label='20 Günlük Hareketli Ortalama')
        
        # Grafik özelliklerini ayarla
        plt.title('THYAO Kapanış Fiyatı Trendi ve Hareketli Ortalamalar', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Zaman', fontsize=12, fontweight='bold')
        plt.ylabel('Fiyat (TL)', fontsize=12, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=11, loc='upper left')
        
        # X ekseni etiketlerini optimize et
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Grafiği kaydet
        trend_plot_path = DESKTOP_PATH / "THYAO_closing_price_trend.png"
        plt.savefig(trend_plot_path, dpi=300, bbox_inches='tight', facecolor='white')
        
        # Grafiği ekranda göster
        plt.show()
        plt.close()
        
        print(f"    [OK] Kapanış fiyatı trendi kaydedildi: {trend_plot_path}")
        
        # 2. Günlük getiri dağılımı (histogram ve normal dağılım analizi)
        print(f"  Günlük getiri dağılımı çiziliyor...")
        
        plt.figure(figsize=(12, 8))
        
        # Histogram
        if 'daily_return' in df.columns:
            # NaN değerleri temizle
            daily_returns_clean = df['daily_return'].dropna()
            
            if len(daily_returns_clean) > 0:
                # Histogram çiz
                plt.hist(daily_returns_clean, bins=50, alpha=0.7, color='#2E86AB', edgecolor='black', linewidth=0.5)
                
                # Normal dağılım eğrisi ekle
                import numpy as np
                from scipy import stats
                
                # Normal dağılım parametreleri
                mu = daily_returns_clean.mean()
                sigma = daily_returns_clean.std()
                
                # Normal dağılım eğrisi
                x = np.linspace(daily_returns_clean.min(), daily_returns_clean.max(), 100)
                y = stats.norm.pdf(x, mu, sigma) * len(daily_returns_clean) * (daily_returns_clean.max() - daily_returns_clean.min()) / 50
                
                plt.plot(x, y, 'r-', linewidth=2, label=f'Normal Dağılım (μ={mu:.4f}, σ={sigma:.4f})')
                
                # İstatistik bilgileri
                plt.axvline(mu, color='red', linestyle='--', alpha=0.8, label=f'Ortalama: {mu:.4f}')
                plt.axvline(mu + sigma, color='orange', linestyle=':', alpha=0.8, label=f'+1σ: {mu + sigma:.4f}')
                plt.axvline(mu - sigma, color='orange', linestyle=':', alpha=0.8, label=f'-1σ: {mu - sigma:.4f}')
                
                # Grafik özelliklerini ayarla
                plt.title('THYAO Günlük Getiri Dağılımı', fontsize=16, fontweight='bold', pad=20)
                plt.xlabel('Günlük Getiri', fontsize=12, fontweight='bold')
                plt.ylabel('Frekans', fontsize=12, fontweight='bold')
                plt.grid(True, alpha=0.3)
                plt.legend(fontsize=11, loc='upper right')
                
                # İstatistik bilgilerini ekle
                stats_text = f'Toplam Gözlem: {len(daily_returns_clean)}\nOrtalama: {mu:.4f}\nStd: {sigma:.4f}\nMin: {daily_returns_clean.min():.4f}\nMax: {daily_returns_clean.max():.4f}'
                plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, fontsize=10, 
                        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
                
                plt.tight_layout()
                
                # Grafiği kaydet
                histogram_plot_path = DESKTOP_PATH / "THYAO_daily_return_distribution.png"
                plt.savefig(histogram_plot_path, dpi=300, bbox_inches='tight', facecolor='white')
                
                # Grafiği ekranda göster
                plt.show()
                plt.close()
                
                print(f"    [OK] Günlük getiri dağılımı kaydedildi: {histogram_plot_path}")
                
                # İstatistik özeti
                print(f"    Günlük getiri istatistikleri:")
                print(f"      Ortalama: {mu:.4f}")
                print(f"      Standart Sapma: {sigma:.4f}")
                print(f"      Minimum: {daily_returns_clean.min():.4f}")
                print(f"      Maksimum: {daily_returns_clean.max():.4f}")
                print(f"      Toplam gözlem: {len(daily_returns_clean)}")
            else:
                print(f"    ⚠ daily_return sütununda veri bulunamadı")
        else:
            print(f"    ⚠ daily_return sütunu bulunamadı")
        
        # 3. Gerçek vs. Tahmin grafiği (model performansı)
        print(f"  Gerçek vs. Tahmin grafiği çiziliyor...")
        
        try:
            # Model tahminlerini al (eğer mevcut ise)
            if 'lr_test_pred' in locals() and 'knn_test_pred' in locals():
                plt.figure(figsize=(14, 10))
                
                # Alt grafik 1: Linear Regression
                plt.subplot(2, 1, 1)
                plt.scatter(y_test, lr_test_pred, alpha=0.6, color='#2E86AB', s=50)
                
                # Mükemmel tahmin çizgisi (y=x)
                min_val = min(y_test.min(), lr_test_pred.min())
                max_val = max(y_test.max(), lr_test_pred.max())
                plt.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Mükemmel Tahmin (y=x)')
                
                plt.title('Linear Regression: Gerçek vs. Tahmin', fontsize=14, fontweight='bold')
                plt.xlabel('Gerçek Kapanış Fiyatı (TL)', fontsize=12)
                plt.ylabel('Tahmin Edilen Fiyat (TL)', fontsize=12)
                plt.grid(True, alpha=0.3)
                plt.legend()
                
                # R² değerini ekle
                plt.text(0.05, 0.95, f'R² = {lr_test_r2:.4f}', transform=plt.gca().transAxes, 
                        fontsize=12, bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
                
                # Alt grafik 2: KNN Regressor
                plt.subplot(2, 1, 2)
                plt.scatter(y_test, knn_test_pred, alpha=0.6, color='#A23B72', s=50)
                
                # Mükemmel tahmin çizgisi (y=x)
                plt.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Mükemmel Tahmin (y=x)')
                
                plt.title('KNN Regressor: Gerçek vs. Tahmin', fontsize=14, fontweight='bold')
                plt.xlabel('Gerçek Kapanış Fiyatı (TL)', fontsize=12)
                plt.ylabel('Tahmin Edilen Fiyat (TL)', fontsize=12)
                plt.grid(True, alpha=0.3)
                plt.legend()
                
                # R² değerini ekle
                plt.text(0.05, 0.95, f'R² = {knn_test_r2:.4f}', transform=plt.gca().transAxes, 
                        fontsize=12, bbox=dict(boxstyle='round', facecolor='lightpink', alpha=0.8))
                
                plt.tight_layout()
                
                # Grafiği kaydet
                prediction_plot_path = DESKTOP_PATH / "THYAO_real_vs_prediction.png"
                plt.savefig(prediction_plot_path, dpi=300, bbox_inches='tight', facecolor='white')
                
                # Grafiği ekranda göster
                plt.show()
                plt.close()
                
                print(f"    [OK] Gerçek vs. Tahmin grafiği kaydedildi: {prediction_plot_path}")
                
                # Model performans özeti
                print(f"    Model performans özeti:")
                print(f"      Linear Regression: R²={lr_test_r2:.4f}, RMSE={lr_test_rmse:.4f}, MAE={lr_test_mae:.4f}")
                print(f"      KNN Regressor: R²={knn_test_r2:.4f}, RMSE={knn_test_rmse:.4f}, MAE={knn_test_mae:.4f}")
                
            else:
                print(f"    ⚠ Model tahminleri bulunamadı, grafik çizilemedi")
                
        except Exception as e:
            print(f"    ⚠ Gerçek vs. Tahmin grafiği çizilemedi: {e}")
        
        # 4. KNN k değerleri karşılaştırma grafiği
        print(f"  KNN k değerleri karşılaştırma grafiği çiziliyor...")
        
        try:
            # KNN k değerleri sonuçlarını al (eğer mevcut ise)
            if 'knn_results_list' in locals() and len(knn_results_list) > 0:
                plt.figure(figsize=(14, 10))
                
                # Alt grafik 1: R² skorları
                plt.subplot(2, 2, 1)
                k_values = [result['k'] for result in knn_results_list]
                r2_scores = [result['r2'] for result in knn_results_list]
                
                plt.plot(k_values, r2_scores, 'o-', linewidth=2, markersize=8, color='#A23B72')
                plt.axhline(y=0, color='red', linestyle='--', alpha=0.7, label='R² = 0 (Random)')
                
                # En iyi k değerini işaretle
                best_k_result = max(knn_results_list, key=lambda x: x['r2'])
                plt.axvline(x=best_k_result['k'], color='green', linestyle=':', linewidth=2, 
                           label=f'En iyi k = {best_k_result["k"]}')
                
                plt.title('KNN: k Değerine Göre R² Skoru', fontsize=14, fontweight='bold')
                plt.xlabel('k (n_neighbors)', fontsize=12)
                plt.ylabel('R² Skoru', fontsize=12)
                plt.grid(True, alpha=0.3)
                plt.legend()
                
                # Alt grafik 2: RMSE skorları
                plt.subplot(2, 2, 2)
                rmse_scores = [result['rmse'] for result in knn_results_list]
                
                plt.plot(k_values, rmse_scores, 's-', linewidth=2, markersize=8, color='#F18F01')
                plt.axvline(x=best_k_result['k'], color='green', linestyle=':', linewidth=2)
                
                plt.title('KNN: k Değerine Göre RMSE', fontsize=14, fontweight='bold')
                plt.xlabel('k (n_neighbors)', fontsize=12)
                plt.ylabel('RMSE', fontsize=12)
                plt.grid(True, alpha=0.3)
                
                # Alt grafik 3: MAE skorları
                plt.subplot(2, 2, 3)
                mae_scores = [result['mae'] for result in knn_results_list]
                
                plt.plot(k_values, mae_scores, '^-', linewidth=2, markersize=8, color='#2E86AB')
                plt.axvline(x=best_k_result['k'], color='green', linestyle=':', linewidth=2)
                
                plt.title('KNN: k Değerine Göre MAE', fontsize=14, fontweight='bold')
                plt.xlabel('k (n_neighbors)', fontsize=12)
                plt.ylabel('MAE', fontsize=12)
                plt.grid(True, alpha=0.3)
                
                # Alt grafik 4: Tüm metrikler karşılaştırması
                plt.subplot(2, 2, 4)
                
                # Metrikleri normalize et (0-1 arasına)
                r2_norm = [(r2 - min(r2_scores)) / (max(r2_scores) - min(r2_scores)) for r2 in r2_scores]
                rmse_norm = [(rmse - min(rmse_scores)) / (max(rmse_scores) - min(rmse_scores)) for rmse in rmse_scores]
                mae_norm = [(mae - min(mae_scores)) / (max(mae_scores) - min(mae_scores)) for mae in mae_scores]
                
                plt.plot(k_values, r2_norm, 'o-', linewidth=2, markersize=8, color='#A23B72', label='R² (normalize)')
                plt.plot(k_values, rmse_norm, 's-', linewidth=2, markersize=8, color='#F18F01', label='RMSE (normalize)')
                plt.plot(k_values, mae_norm, '^-', linewidth=2, markersize=8, color='#2E86AB', label='MAE (normalize)')
                plt.axvline(x=best_k_result['k'], color='green', linestyle=':', linewidth=2)
                
                plt.title('KNN: Tüm Metrikler Karşılaştırması', fontsize=14, fontweight='bold')
                plt.xlabel('k (n_neighbors)', fontsize=12)
                plt.ylabel('Normalize Edilmiş Skorlar', fontsize=12)
                plt.grid(True, alpha=0.3)
                plt.legend()
                
                plt.tight_layout()
                
                # Grafiği kaydet
                knn_comparison_plot_path = DESKTOP_PATH / "THYAO_knn_k_comparison.png"
                plt.savefig(knn_comparison_plot_path, dpi=300, bbox_inches='tight', facecolor='white')
                
                # Grafiği ekranda göster
                plt.show()
                plt.close()
                
                print(f"    [OK] KNN k değerleri karşılaştırma grafiği kaydedildi: {knn_comparison_plot_path}")
                
                # K değerleri özeti
                print(f"    K değerleri özeti:")
                print(f"      En iyi k: {best_k_result['k']}")
                print(f"      En iyi R²: {best_k_result['r2']:.4f}")
                print(f"      En iyi RMSE: {best_k_result['rmse']:.4f}")
                print(f"      En iyi MAE: {best_k_result['mae']:.4f}")
                
            else:
                print(f"    ⚠ KNN k değerleri sonuçları bulunamadı, grafik çizilemedi")
                
        except Exception as e:
            print(f"    ⚠ KNN k değerleri karşılaştırma grafiği çizilemedi: {e}")
        

        
    except ImportError as e:
        print(f"  ⚠ Gerekli kütüphaneler bulunamadı: {e}")
        print(f"    Grafikler oluşturulamadı. matplotlib, seaborn ve scipy kurulumu gerekli.")
    except Exception as e:
        print(f"  ✗ Grafik oluşturma sırasında hata: {e}")
        print(f"    Grafikler oluşturulamadı.")

    # 12. VERİ TEMİZLEME VE KAYDETME
    
    # Gereksiz sütunları kaldır ve temizlenmiş veriyi kaydet
    cleaned_df, dropped_cols, missing_cols = remove_columns_from_dataframe(
        df, COLUMNS_TO_REMOVE
    )

    # Temizlenmiş veriyi CSV olarak kaydet
    try:
        cleaned_df.to_csv(OUTPUT_CSV_PATH, index=False, encoding="utf-8-sig")
        print(f"\nVERİ TEMİZLEME VE KAYDETME TAMAMLANDI")
    except Exception as e:
        print(f"Temizlenmiş CSV kaydedilirken hata oluştu: {e}")
        return

    # Temizleme işlemi özeti
    print(f"Silinen sütun sayısı: {len(dropped_cols)}")

    print(f"Temizlenmiş dosya kaydedildi: {OUTPUT_CSV_PATH}")



if __name__ == "__main__":
    main()
