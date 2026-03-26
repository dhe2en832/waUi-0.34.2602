# Changelog Generator Tool

Automatic changelog generator for WACSA-MD2 UI project.

## 📋 Overview

The changelog generator automatically creates daily changelog files based on:
- Git commits from today
- Unstaged file changes
- File analysis (new functions, classes, etc.)

## 🚀 Usage

### Basic Usage

```bash
# Generate changelog for today
python custom/scripts/generate_changelog.py
```

### Output

The tool generates a markdown file at:
```
custom/docs/changelog/daily/codeChange-YYYYMMDD.md
```

Example: `codeChange-20260326.md`

## 📊 Features

### 1. **Automatic Categorization**

Changes are automatically categorized into:

- ✨ **Features** - New features and additions
- 🐞 **Fixes** - Bug fixes and error corrections
- 📖 **Documentation** - Documentation updates
- 🧪 **Tests** - Test files and testing
- 🎨 **UI/UX** - User interface changes
- 🔌 **API** - API client and integration
- ⚙️ **Config** - Configuration changes
- 📦 **Build** - Build scripts and dependencies
- 🧹 **Cleanup** - Code cleanup and organization
- ⚙️ **Others** - Refactoring and other changes

### 2. **Commit Analysis**

For each commit, the tool shows:
- Commit message
- Commit hash (short)
- Date and time
- List of modified files
- New functions and classes (for Python files)

### 3. **Unstaged Changes**

The tool also detects unstaged changes and includes them in the changelog with:
- List of modified files
- Automatic message generation based on file types

### 4. **File Analysis**

For Python files, the tool analyzes:
- New functions added
- New classes added
- Number of additions/deletions

## 📝 Example Output

```markdown
# Code Changes - 2026-03-26

**Generated**: 2026-03-26 16:20:15

---

## 📊 Summary

- **Total Changes**: 4
- **Categories**: 2
- **Files Modified**: 15

## ✨ Features

### feat: add WhatsApp-like message UI

**Commit**: `abc1234`  
**Date**: 2026-03-26 14:30:00

**Files**:
- `src/ui/components/chat_view.py`
- `src/ui/components/message_bubble.py`
- `src/ui/components/chat_list.py`

**Changes in `src/ui/components/message_bubble.py`**:
- New functions: MessageBubble, DateSeparator
- New classes: MessageBubble, DateSeparator

---

## 🧹 Cleanup

### 🔄 Unstaged Changes

**Files**:
- `custom/scripts/generate_changelog.py`
- `README.md`

---
```

## 🔧 How It Works

### 1. Git Commit Detection

```python
# Gets all commits from today
git log --since="2026-03-26 00:00:00" --until="2026-03-26 23:59:59"
```

### 2. Unstaged Changes Detection

```python
# Checks for modified files
git status --porcelain
```

### 3. File Analysis

```python
# Analyzes diff for each file
git diff HEAD <file>
```

### 4. Categorization Logic

The tool uses pattern matching to categorize commits:

- **Message keywords**: `feat:`, `fix:`, `add`, `new`, `bug`, etc.
- **File patterns**: `.py`, `.md`, `api/`, `ui/`, `test/`, etc.
- **Content analysis**: Functions, classes, imports, etc.

## 📅 Workflow

### Recommended Workflow

1. **Make changes** to your code
2. **Commit changes** with descriptive messages
3. **Generate changelog**:
   ```bash
   python custom/scripts/generate_changelog.py
   ```
4. **Review changelog**:
   ```bash
   # Open the generated file
   code custom/docs/changelog/daily/codeChange-YYYYMMDD.md
   ```
5. **Stage and commit changelog**:
   ```bash
   git add custom/docs/changelog/daily/codeChange-YYYYMMDD.md
   git commit -m "docs: add daily changelog"
   ```

### Best Practices

1. **Run before staging** - Generate changelog before staging files to capture all changes
2. **Descriptive commits** - Use clear commit messages for better categorization
3. **Daily generation** - Run once per day to keep changelog organized
4. **Review output** - Always review generated changelog for accuracy

## 🎯 Commit Message Conventions

For best categorization, use these prefixes:

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation
- `test:` - Tests
- `ui:` - UI changes
- `api:` - API changes
- `config:` - Configuration
- `build:` - Build/dependencies
- `chore:` - Maintenance
- `refactor:` - Code refactoring

### Examples

```bash
git commit -m "feat: add login window component"
git commit -m "fix: resolve authentication token issue"
git commit -m "docs: update README with new features"
git commit -m "ui: improve message bubble styling"
git commit -m "chore: clean up old files"
```

## 🔍 Troubleshooting

### No commits found

**Issue**: "No commits found for today"

**Solution**: 
- Make sure you have commits today
- Check git log manually: `git log --since="today"`
- Tool will still capture unstaged changes

### Encoding errors (Windows)

**Issue**: Unicode encoding errors in console

**Solution**: 
- Script automatically handles Windows encoding
- If issues persist, use Git Bash or WSL

### Permission errors

**Issue**: Cannot write to changelog directory

**Solution**:
```bash
# Create directory manually
mkdir -p custom/docs/changelog/daily
```

## 📦 Dependencies

The tool uses only Python standard library:
- `os` - File operations
- `sys` - System operations
- `subprocess` - Git commands
- `datetime` - Date/time handling
- `pathlib` - Path operations
- `re` - Regular expressions
- `collections` - Data structures

No external dependencies required!

## 🔄 Migration from Node.js

The original Node.js script (`generate-changelog.cjs`) has been converted to Python for:
- **Consistency** - Match project language (Python)
- **Simplicity** - No Node.js dependency needed
- **Integration** - Better integration with Python project
- **Maintenance** - Easier to maintain alongside main code

The Python version provides the same functionality with improvements:
- Better Windows console support
- Cleaner code structure
- More detailed file analysis
- Enhanced categorization

## 📝 Notes

- Changelog files are stored in `custom/docs/changelog/daily/`
- Each day gets a new file: `codeChange-YYYYMMDD.md`
- Files are in Markdown format for easy reading
- Generated content can be manually edited if needed
- Tool is safe to run multiple times (overwrites same day's file)

---

**Version**: 1.0.0  
**Language**: Python 3.8+  
**License**: MIT
