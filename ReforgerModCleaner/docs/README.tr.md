# Reforger Mod Cleaner

Türkçe · **[English](../README.md)**

> **Resmî olmayan, hayran yapımı bir araçtır.** Bohemia Interactive a.s. ile bağlantısı yoktur ve onun tarafından onaylanmamıştır. Arma, Arma Reforger, Bohemia Interactive ve ilgili tüm logo ve tasarımlar Bohemia Interactive a.s.'nin ticari markaları veya tescilli ticari markalarıdır.

Arma Reforger **istemci** mod klasörü (`Documents\My Games\ArmaReforger\addons`) için bir Windows masaüstü aracı. İndirdiğin Workshop modlarını listeler ve onları oynadığın sunucuya göre etiketlemeni sağlar. Hangi modun başka modlara gerekli olduğunu gösterir. Artık kullanmadıklarını da Geri Dönüşüm Kutusu'na gönderir.

Arayüz **Türkçe ve İngilizce** kullanılabilir. Program Windows'un diliyle açılır; araç çubuğundaki **Dil** düğmesi dili istediğin an değiştirir.

<!-- Yayından önce ekran görüntüsü ekle: docs/screenshot.png olarak kaydet ve bu yorum satırını sil.
![Ekran görüntüsü](screenshot.png)
-->

## Özellikler

- **Mod listesi**: isim, sürüm, boyut, tarih ve sunucu etiketi sütunları. Sıralamak için sütun başlığına tıkla.
- **Sunucu etiketleri**:
  - Etiketlemek için satıra çift tıkla ya da birden çok satırı seçip toplu etiketle.
  - Bir mod listesi veya oyun içi mod preset JSON'u yapıştırırsan eşleşen tüm modlar etiketlenir.
  - Sunucu `config.json` dosyalarının bulunduğu klasörü gösterirsen her açılışta modlar otomatik etiketlenir. Açılışta elle verdiğin etiketlerin üzerine yazılmaz; klasörü ilk seçtiğinde üzerine yazılıp yazılmayacağı sorulur.
- **Bağımlılık takibi**: her modun `ServerData.json` dosyasındaki `dependencies` alanı okunur. Başka modların ihtiyaç duyduğu modlar ⛓ ile işaretlenir; böyle bir modu silmeye kalkarsan uyarı çıkar.
- **Boyut haritası**: disk kullanımını sunucuya göre renklendirilmiş bir treemap olarak gösterir.
- **Güvenli silme**: modlar kalıcı olarak silinmez, Geri Dönüşüm Kutusu'na gider. Oyun açıksa uyarı verir.
- **Çevrimdışı**: internete bağlanmaz, telemetri yoktur.

## Gereksinimler

- Windows 10 veya 11
- Exe'yi çalıştırmak için başka hiçbir şey gerekmez
- Kaynak koddan çalıştırmak ya da exe'yi kendin derlemek için Python 3.9 veya üstü

## Kurulum

### Seçenek 1: Hazır exe

[Releases](../../../releases/latest) sayfasından `ReforgerModCleaner.exe` dosyasını indir ve çift tıkla. Python dahil hiçbir şey kurman gerekmez; gereken her şey exe'nin içindedir. Exe, GitHub Actions tarafından bu depodaki kaynak koddan otomatik olarak derlenir; bkz. [`.github/workflows/build.yml`](../.github/workflows/build.yml).

**Windows SmartScreen / antivirüs uyarısı:** exe kod imzalı değildir ve PyInstaller ile paketlenmiştir. Bu iki durum sıklıkla "Windows bilgisayarınızı korudu" uyarısına ya da yanlış pozitif antivirüs tespitine yol açar. Çalıştırmak için *Ek bilgi → Yine de çalıştır* adımlarını izle. Exe'ye güvenmiyorsan Seçenek 2 veya 3'ü kullan; ikisi de aynı programı bu kaynak koddan üretir. Her sürümde bir `SHA256.txt` dosyası bulunur; indirdiğin dosyayı şu komutla doğrulayabilirsin:

```
certutil -hashfile ReforgerModCleaner.exe SHA256
```

### Seçenek 2: Exe'yi kendin derle

Depoyu indir, sonra içindeki `build.bat` dosyasına çift tıkla. Çıktı `dist\ReforgerModCleaner.exe` konumuna yazılır.

### Seçenek 3: Kaynak koddan çalıştır

```
pip install -r requirements.txt
pythonw reforger_mod_cleaner.py
```

`pythonw` konsol penceresi açmadan çalıştırır. Hataları konsolda görmek istersen `python` kullan.

## Kullanım

1. `addons` klasörü otomatik bulunur; Belgeler klasörü OneDrive'a yönlendirilmiş olsa da bulunur. Bulunamazsa klasörü **Klasör** düğmesiyle seç.
2. Oynadığın sunucuların modlarını etiketle:
   - Oyun içinde mod preset'ini aç, JSON'unu kopyala. **Otomatik Etiketle** penceresine yapıştır ve bir sunucu adı yaz.
   - Ya da sunucu `config.json` dosyalarının bulunduğu klasörü **Sunucu Config Klasörü** ile göster.
3. **Etiketsizleri Seç**, etiketsiz olan ve hiçbir modun bağımlı olmadığı modların hepsini seçer. Bu satırlar kırmızı görünür. Devam etmeden önce seçimi gözden geçir.
4. **Seçilenleri Sil**, seçili modları Geri Dönüşüm Kutusu'na gönderir. Yanlışlıkla bir şey sildiysen oradan geri yükleyebilirsin.

Kırmızı satır, o modun silinmesinin **güvenli olduğu** anlamına gelmez; sadece henüz etiketlemediğin anlamına gelir. Önce sunucularının modlarını etiketle, temizliği ondan sonra yap.

### Modlar nasıl tanınır

`addons` klasöründeki her alt klasörde bir `ServerData.json` dosyası bulunur. Bu dosyada modun `id`, `name`, `revision.version` ve `revision.dependencies` alanları yer alır; araç bu alanları okur. Etiket eşleştirmesi yalnızca mod ID'sinin **birebir** ya da mod adının **birebir** eşleşmesiyle yapılır, kısmi isimlerle yapılmaz: "ACE", "Peace Keeper" ile eşleşmez.

## Veriler ve gizlilik

| Ne | Nerede |
|---|---|
| Etiketler ve ayarlar (dil, arka plan yolu, sunucu config klasörü) | `%APPDATA%\ReforgerModCleaner\` |
| Hata günlüğü | `%TEMP%\ReforgerModCleaner.log` |

Bunların dışında hiçbir şey yazılmaz ve hiçbir yere veri gönderilmez. **Yerel Veriyi Sil** düğmesi etiketleri ve ayarları siler. Mod dosyalarına dokunmaz.

**Kaldırma:** exe dosyasını, `%APPDATA%\ReforgerModCleaner\` klasörünü ve günlük dosyasını sil.

## Bilinen sınırlamalar

- Pencere boyutu sabittir. 1366×768 ekrana sığacak şekilde otomatik küçülür, ama daha küçük ekranlarda kırpılır.
- Windows görüntü ölçeklendirmesi %125 veya üzerindeyse pencereyi Windows büyütür; bu yüzden görüntü hafif bulanık olabilir.
- Yalnızca istemcinin `addons` klasörü desteklenir. Dedicated sunucu profil klasörleri taranmaz.
- Onay pencerelerindeki Evet/Hayır düğmeleri uygulamadaki dil ayarını değil, Windows'un dilini izler.

## Depo yapısı

| Yol | İçerik |
|---|---|
| `reforger_mod_cleaner.py` | Uygulamanın tamamı (tek dosya) |
| `assets/` | Exe'ye gömülen arka plan görseli ve ikon |
| `tests/` | Otomatik testler (pencere açmaz) |
| `docs/` | Türkçe README, değişiklik günlüğü, üçüncü taraf bildirimleri |
| `build.bat` | Exe'yi bilgisayarında derler |
| `.github/workflows/build.yml` | Exe'yi GitHub'da derler, açılışını test eder ve yayınlar |
| `requirements.txt`, `requirements-dev.txt` | Çalışma ve geliştirme bağımlılıkları |

## Geliştirme

```
pip install -r requirements.txt -r requirements-dev.txt
python -m pyflakes reforger_mod_cleaner.py tests
python -m pytest -q tests
```

Testler pencere açmaz. Veri fonksiyonlarını, tarama ve silme akışlarını, iki dili ve pencereyi kuran kodun tamamını sahte bir Tk ile test eder.

Arayüz metni eklemek ya da değiştirmek için `reforger_mod_cleaner.py` içindeki `STRINGS` tablosunu düzenle. İki dilde de aynı anahtarlar bulunmalıdır; bunu bir test denetler.

### Sürüm yayınlama (komut satırı gerekmez)

1. `reforger_mod_cleaner.py` dosyasındaki `APP_VERSION` değerini güncelle, `docs/CHANGELOG.md` dosyasına bir giriş ekle ve commit et.
2. GitHub'da **Releases → Draft a new release** yolunu izle, `v<APP_VERSION>` biçiminde bir etiket oluştur (örneğin `v1.0.0`) ve **Publish release**'e tıkla.
3. Bundan sonrası birkaç dakika içinde GitHub Actions'ta otomatik ilerler: testler çalışır, exe derlenir, açılıp açılmadığı kontrol edilir, sonra `ReforgerModCleaner.exe` ve `SHA256.txt` sürüme eklenir. Etiket ile `APP_VERSION` uyuşmazsa derleme durur.

`main` dalına yapılan her push da derlenir; o exe'yi **Actions** sekmesinde ilgili çalıştırmanın **Artifacts** bölümünden indirebilirsin.

## Sorun bildirme

Bir issue aç ve `%TEMP%\ReforgerModCleaner.log` dosyasını ekle. Günlükte yalnızca klasör yolları ve mod adları bulunur. Klasör yollarında Windows kullanıcı adın da geçer (`C:\Users\<ad>`); istersen paylaşmadan önce sil.

## Lisans

Kod [MIT](../LICENSE) lisansıyla yayınlanır. Hazır exe, kendi lisanslarına tabi olmaya devam eden üçüncü taraf bileşenleri içerir; ayrıntılar için [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) dosyasına bak. Arka plan ve ikon görselleri yazar tarafından yapay zekâ ile üretilmiştir ve aynı MIT lisansıyla yayınlanır. Sürüm geçmişi için [değişiklik günlüğüne](CHANGELOG.md) bak.
