# Scripts

Utility scripts for WACSA-MD2 UI project.

## 📁 Available Scripts

### 📝 Changelog Generator

**File**: `generate_changelog.py`

Automatically generates daily changelog from git commits and file changes.

**Usage**:
```bash
python custom/scripts/generate_changelog.py
```

**Features**:
- Automatic categorization of changes
- Git commit analysis
- Unstaged changes detection
- File diff analysis
- Markdown output

**Documentation**: See [CHANGELOG_TOOL.md](../docs/development/CHANGELOG_TOOL.md)

---

## 🚀 Quick Start

### Generate Today's Changelog

```bash
# From project root
python custom/scripts/generate_changelog.py
```

Output: `custom/docs/changelog/daily/codeChange-YYYYMMDD.md`

---

## 📚 More Information

For detailed documentation on each script, see:
- [Changelog Tool Documentation](../docs/development/CHANGELOG_TOOL.md)
- [Development Guide](../docs/development/)

---

**Last Updated**: March 26, 2026
