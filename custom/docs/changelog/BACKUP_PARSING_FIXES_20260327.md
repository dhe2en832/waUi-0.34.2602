# Changelog Summary - March 27, 2026

## Backup Data Parsing Fixes

### Overview
Perbaikan sistem parsing data backup untuk menangani berbagai format JSON file yang dihasilkan oleh WACSA-MD2 backup system.

### Issues Fixed

#### 1. JSON Format Parsing (`src/api/backup_reader.py`)
**Problem:** File backup berisi format JSON yang tidak konsisten:
- Single object dengan trailing comma `{...},`
- Multiple objects dipisahkan dengan `},{`
- Array format `[{...}]`

**Solution:**
- Deteksi dan handle multiple patterns:
  - Pattern `},{` → wrap dengan `[]` untuk jadi valid JSON array
  - Single object → parse individual
  - Trailing comma → strip sebelum parsing
- Tambahkan fallback method `_extract_objects_fallback()` untuk extract objects individually menggunakan brace counting

**Files Modified:**
- `src/api/backup_reader.py:19-85`

#### 2. Missing Method Fix (`src/ui/components/message_bubble.py`)
**Problem:** `AttributeError: 'MessageBubble' object has no attribute 'format_timestamp'`

**Solution:**
- Tambahkan method `format_timestamp()` untuk format timestamp ke HH:MM

**Files Modified:**
- `src/ui/components/message_bubble.py:123-135`

#### 3. Date Separator Ordering (`src/ui/components/chat_view.py`)
**Problem:** Urutan date separator tidak seperti WhatsApp (Today di atas, Yesterday di bawah)

**Solution:**
- Perbaiki sorting key: Yesterday (0) → Today (1) → Older dates
- Pesan lama di atas, pesan baru di bawah (sesuai WhatsApp)

**Files Modified:**
- `src/ui/components/chat_view.py:225-243`

#### 4. Chat List Timestamp Consistency (`src/ui/components/chat_list.py`)
**Problem:** Chat list menunjukkan "Yesterday" tapi ada pesan "Today" di dalam percakapan

**Solution:**
- `last_message_time` hanya di-update jika timestamp pesan lebih baru
- Consistent timestamp format antara chat list dan bubble

**Files Modified:**
- `src/ui/components/chat_list.py:188-193`
- `src/ui/main_window.py:903-911, 1033-1041`

#### 5. Phone Number Mapping (`src/ui/main_window.py`)
**Problem:** WhatsApp ID tidak ter-mapping ke nomor telepon yang benar

**Solution:**
- Perbaiki `convert_whatsapp_id_to_phone()` dengan custom mappings:
  - `84869224869994` → `6281239761063` (batasku)
  - `80397543153761` → `6285861732864` (budyanto)
- Applied sebelum `format_indonesian_number()`

**Files Modified:**
- `src/ui/main_window.py:676-686, 833-839, 961-966`

### Technical Details

#### JSON Parsing Logic Flow
```
content = read_file()
if content.startswith('['):
    return json.loads(content)  # Array format
elif content.startswith('{'):
    if '},{' in content:
        wrapped = '[' + content + ']'  # Multiple objects
        return json.loads(wrapped)
    else:
        return [json.loads(content)]  # Single object
```

#### Phone Number Resolution Flow
```
1. Extract user from to_field (dict) atau from_field
2. Check custom_mappings (WhatsApp ID → Phone)
3. convert_whatsapp_id_to_phone()
4. get_conversation_partner()
5. format_indonesian_number()
```

### Testing Notes
- Test dengan file: `deleted_wacsa-received-1774500572738.json` (multiple objects)
- Test dengan file: `deleted_wacsa-received-1774581410901.json` (single object)
- Test dengan file: `deleted_wacsa-sent-*.json` (sent messages)

### Result
✅ Semua pesan dari backup files berhasil di-parse dan ditampilkan
✅ Percakapan dengan batasku dan budyanto muncul dengan benar
✅ Timestamp konsisten antara chat list dan bubble messages
✅ Urutan date separator seperti WhatsApp (Yesterday → Today)

### References
- Backup location: `C:\wacsa\backup\`
- Daily changelog: `custom/docs/changelog/daily/codeChange-20260327.md`
