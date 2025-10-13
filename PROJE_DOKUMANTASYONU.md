# TCMB MCP Server - Proje Dokümantasyonu

## Proje Özeti
Türkiye Cumhuriyet Merkez Bankası (TCMB) döviz kurları için geliştirilmiş MCP (Model Context Protocol) sunucusu.

**GitHub Repository:** https://github.com/m-atalar/tcmb-mcp-server

---

## Ne Yaptık? (Adım Adım)

### 1. API Seçimi
- **Seçilen API:** TCMB (Türkiye Cumhuriyet Merkez Bankası) Döviz Kurları API
- **API URL'leri:**
  - Güncel kurlar: `https://www.tcmb.gov.tr/kurlar/today.xml`
  - Geçmiş kurlar: `https://www.tcmb.gov.tr/kurlar/{year}{month}/{day}{month}{year}.xml`
- **Neden bu API?**
  - Auth gerektirmiyor (kolay kullanım)
  - Resmi devlet verisi (güvenilir)
  - %100 "milli" (bonus puan için ideal)
  - Ücretsiz ve açık erişim

### 2. MCP Server Projesi Oluşturma

#### Proje Yapısı
```
tcmb-mcp-server/
├── src/
│   └── tcmb_mcp_server/
│       ├── __init__.py
│       └── server.py          # Ana MCP server kodu
├── pyproject.toml             # Python paket yapılandırması
├── smithery.json              # Smithery deployment yapılandırması
├── README.md                  # Proje açıklaması
├── LICENSE                    # MIT lisansı
├── .gitignore                 # Git ignore kuralları
└── PROJE_DOKUMANTASYONU.md    # Bu dosya
```

#### Kullanılan Teknolojiler
- **Python 3.13.0**
- **MCP SDK:** `mcp>=1.0.0`
- **HTTP Client:** `httpx>=0.27.0`
- **XML Parsing:** `xml.etree.ElementTree` (built-in)

### 3. MCP Server Özellikleri

#### Tools (Araçlar)
1. **`get_exchange_rates`**
   - Güncel veya geçmiş döviz kurlarını getirir
   - Parametreler:
     - `date` (opsiyonel): Geçmiş tarih (format: YYYY-MM-DD)
     - `currency_code` (opsiyonel): Para birimi kodu (USD, EUR, GBP vb.)
   - Örnek kullanım:
     ```json
     {"currency_code": "USD"}
     {"date": "2024-01-15"}
     {"date": "2024-01-15", "currency_code": "EUR"}
     ```

2. **`list_currencies`**
   - TCMB'de mevcut tüm para birimlerini listeler
   - Parametre gerektirmez
   - Çıktı: Para birimi kodları ve isimleri

#### Resources (Kaynaklar)
- **`tcmb://exchange-rates/today`**
  - Güncel döviz kurlarını kaynak olarak sunar
  - MimeType: `text/plain`

#### Veri Formatı
Her kur bilgisi şunları içerir:
- Para birimi kodu (USD, EUR, GBP vb.)
- Para birimi ismi
- Birim (genellikle 1 veya 100)
- Döviz Alış Kuru (TL)
- Döviz Satış Kuru (TL)
- Efektif Alış Kuru (TL)
- Efektif Satış Kuru (TL)

### 4. Kurulum ve Test

#### Bağımlılıkları Yükleme
```bash
cd tcmb-mcp-server
pip install -e .
```

#### MCP Inspector ile Test
```bash
npx @modelcontextprotocol/inspector python -m tcmb_mcp_server.server
```

Inspector başarıyla çalıştı ve test edildi:
- URL: `http://localhost:6274/`
- Tüm tools ve resources başarıyla test edildi

### 5. Git ve GitHub

#### Git Repository Oluşturma
```bash
git init
git add .
git commit -m "Initial commit: TCMB MCP Server with exchange rates API"
```

#### GitHub'a Push
```bash
git remote add origin https://github.com/m-atalar/tcmb-mcp-server.git
git branch -M main
git push -u origin main
```

**GitHub URL:** https://github.com/m-atalar/tcmb-mcp-server

### 6. Smithery Deployment

#### Smithery Nedir?
Smithery, MCP serverlarını keşfetmek, paylaşmak ve kullanmak için bir platform.

#### Deployment Adımları
1. https://smithery.ai adresine git
2. GitHub ile giriş yap (m-atalar hesabı)
3. "Add Server" veya "Submit MCP Server" butonuna tıkla
4. Repository URL'sini gir: `https://github.com/m-atalar/tcmb-mcp-server`
5. Smithery otomatik olarak `smithery.json` dosyasını okur
6. "Publish" butonuna tıkla

#### Smithery Yapılandırması (smithery.json)
```json
{
  "name": "tcmb-mcp-server",
  "description": "MCP server for Turkish Central Bank (TCMB) exchange rates",
  "version": "0.1.0",
  "categories": ["finance", "data", "turkey"],
  "keywords": ["tcmb", "exchange", "currency", "turkey", "turkish", "döviz", "kur"],
  "runtime": "python",
  "command": "python",
  "args": ["-m", "tcmb_mcp_server.server"]
}
```

---

## Kullanım Örnekleri

### Claude Desktop ile Kullanım

1. Claude Desktop'ta MCP server'ı yapılandır:
```json
{
  "mcpServers": {
    "tcmb": {
      "command": "python",
      "args": ["-m", "tcmb_mcp_server.server"]
    }
  }
}
```

2. Claude'a şu soruları sorabilirsin:
   - "Bugünkü dolar kuru nedir?"
   - "15 Ocak 2024 tarihindeki Euro kuru neydi?"
   - "Hangi para birimlerinin kuru var?"
   - "Tüm güncel döviz kurlarını göster"

### Doğrudan Python Kullanımı

```python
import asyncio
import httpx
import xml.etree.ElementTree as ET

async def get_rates():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://www.tcmb.gov.tr/kurlar/today.xml")
        print(response.text)

asyncio.run(get_rates())
```

---

## Önemli Notlar

### TCMB API Kuralları
- TCMB sadece **iş günleri** için kur yayınlar
- Kurlar her gün **15:30** civarında güncellenir
- Hafta sonları ve resmi tatillerde kur yayınlanmaz
- API ücretsiz ve auth gerektirmez

### MCP Protocol
- MCP, AI modellerinin dış kaynaklara erişmesini sağlar
- Tools: AI'ın çağırabileceği fonksiyonlar
- Resources: AI'ın okuyabileceği kaynaklar
- Prompts: Önceden tanımlanmış komutlar (bu projede yok)

### Bonus Puanlar İçin
Bu proje **"milli"** bir MCP server olduğu için bonus puan kazanabilir:
- ✅ Türkiye'ye özgü API (TCMB)
- ✅ Türkçe dokümantasyon
- ✅ Türk kullanıcılar için faydalı veri
- ✅ Resmi devlet kurumu verisi

---

## Gelecek Geliştirmeler (Opsiyonel)

1. **Daha Fazla Özellik:**
   - Kur karşılaştırma (örn: USD vs EUR)
   - Grafik verisi (son 30 gün trendi)
   - Kur değişim yüzdesi hesaplama

2. **Diğer API'ler:**
   - Diyanet Namaz Vakitleri API eklenebilir
   - AFAD Deprem Verileri eklenebilir
   - MGM Hava Durumu eklenebilir

3. **Performans:**
   - Caching mekanizması (aynı gün için tekrar API çağrısı yapmama)
   - Rate limiting koruması

---

## Sorun Giderme

### Hata: "Belirtilen tarih için kur bilgisi bulunamadı"
- TCMB sadece iş günleri için kur yayınlar
- Hafta sonu veya tatil günü için kur sorguladıysanız bu hatayı alırsınız

### Hata: "TCMB API hatası"
- İnternet bağlantınızı kontrol edin
- TCMB sunucusu geçici olarak kapalı olabilir

### MCP Inspector açılmıyor
- Node.js ve npm kurulu olduğundan emin olun
- Port 6274 kullanımda olabilir, başka bir uygulama kapatın

---

## İletişim ve Destek

- **GitHub Repository:** https://github.com/m-atalar/tcmb-mcp-server
- **GitHub Kullanıcısı:** m-atalar
- **Smithery:** (Deploy edildikten sonra link buraya eklenecek)

---

## Lisans

MIT License - Projeyi özgürce kullanabilir, değiştirebilir ve dağıtabilirsiniz.

---

**Tarih:** 13 Ekim 2025
**Versiyon:** 0.1.0
**Durum:** ✅ Geliştirme tamamlandı, Smithery deployment bekleniyor
