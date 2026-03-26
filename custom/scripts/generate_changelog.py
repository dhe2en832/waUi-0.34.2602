#!/usr/bin/env python3
"""
Dynamic Changelog Generator
Automatically generates changelog from git commits and file changes
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path
import re
from collections import defaultdict

class ChangelogGenerator:
    """Generate changelog from git commits and file changes"""
    
    def __init__(self):
        self.docs_dir = Path.cwd() / "custom" / "docs" / "changelog" / "daily"
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        
        self.patterns = self.initialize_patterns()
        self.categories = self.initialize_categories()
    
    def initialize_patterns(self):
        """Initialize keyword patterns for categorization"""
        return {
            'function_keywords': {
                'whatsapp': 'WhatsApp functionality',
                'message': 'Message handling',
                'send': 'Message sending',
                'receive': 'Message receiving',
                'media': 'Media handling',
                'api': 'API integration',
                'ui': 'UI components',
                'login': 'Authentication',
                'chat': 'Chat functionality',
                'bubble': 'Message bubbles',
                'list': 'List components',
                'view': 'View components',
                'window': 'Window management',
                'config': 'Configuration',
                'build': 'Build process',
            },
            'change_keywords': {
                'import': 'Add import',
                'def': 'Add function',
                'class': 'Add class',
                'return': 'Add return logic',
                'try': 'Add error handling',
                'except': 'Add exception handling',
                'if': 'Add conditional',
                'for': 'Add loop',
                'ctk.': 'Add CustomTkinter component',
                'tk.': 'Add Tkinter component',
            }
        }
    
    def initialize_categories(self):
        """Initialize changelog categories"""
        return {
            '✨ Features': [],
            '🐞 Fixes': [],
            '📖 Documentation': [],
            '🧪 Tests': [],
            '🎨 UI/UX': [],
            '🔌 API': [],
            '⚙️ Config': [],
            '📦 Build': [],
            '🧹 Cleanup': [],
            '⚙️ Others': []
        }
    
    def categorize_commit(self, commit):
        """Categorize commit based on message and files"""
        message = commit['message'].lower()
        files = commit['files']
        
        # Priority-based categorization
        if any(word in message for word in ['feat:', 'add', 'new', 'implement']):
            return '✨ Features'
        
        if any(word in message for word in ['fix:', 'bug', 'error', 'issue']):
            return '🐞 Fixes'
        
        if any('.md' in f or 'docs/' in f or 'README' in f for f in files):
            return '📖 Documentation'
        
        if any('test' in f or 'spec' in f for f in files):
            return '🧪 Tests'
        
        if any(f.endswith('.py') and any(ui in f for ui in ['ui/', 'main.py', 'login', 'chat', 'bubble']) for f in files):
            return '🎨 UI/UX'
        
        if any('api' in f or 'client' in f for f in files) or 'api' in message:
            return '🔌 API'
        
        if any('build' in f or 'requirements' in f or 'setup' in f for f in files):
            return '📦 Build'
        
        if any('.env' in f or 'config' in f for f in files):
            return '⚙️ Config'
        
        if any(word in message for word in ['clean', 'remove', 'delete', 'organize']):
            return '🧹 Cleanup'
        
        if any(word in message for word in ['refactor:', 'chore:', 'update']):
            return '⚙️ Others'
        
        return '⚙️ Others'
    
    def get_commits_today(self):
        """Get all commits from today"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            git_command = [
                'git', 'log',
                f'--since={today} 00:00:00',
                f'--until={today} 23:59:59',
                '--pretty=format:%H|%s|%ai',
                '--name-only'
            ]
            
            output = subprocess.check_output(git_command, encoding='utf-8', stderr=subprocess.DEVNULL)
            
            commits = []
            lines = output.split('\n')
            current_commit = None
            
            for line in lines:
                if '|' in line:
                    if current_commit:
                        commits.append(current_commit)
                    
                    parts = line.split('|')
                    current_commit = {
                        'hash': parts[0].strip(),
                        'message': parts[1].strip(),
                        'date': parts[2].strip(),
                        'files': []
                    }
                elif line.strip() and current_commit:
                    current_commit['files'].append(line.strip())
            
            if current_commit:
                commits.append(current_commit)
            
            return commits
            
        except subprocess.CalledProcessError:
            print("No commits found for today")
            return []
    
    def get_unstaged_changes(self):
        """Get unstaged changes"""
        try:
            status_output = subprocess.check_output(
                ['git', 'status', '--porcelain'],
                encoding='utf-8',
                stderr=subprocess.DEVNULL
            )
            
            changed_files = [
                line[3:].strip()
                for line in status_output.split('\n')
                if line.strip()
            ]
            
            if changed_files:
                return {
                    'hash': 'UNSTAGED',
                    'message': self.generate_unstaged_message(changed_files),
                    'date': datetime.now().isoformat(),
                    'files': changed_files
                }
            
        except subprocess.CalledProcessError:
            pass
        
        return None
    
    def generate_unstaged_message(self, files):
        """Generate message for unstaged changes"""
        file_types = []
        for file in files:
            if 'main.py' in file:
                file_types.append('main UI')
            elif 'api' in file and file.endswith('.py'):
                file_types.append('API client')
            elif 'build.py' in file:
                file_types.append('build script')
            elif file.endswith('.py'):
                file_types.append('python code')
            elif file.endswith('.md'):
                file_types.append('docs')
            elif 'requirements.txt' in file:
                file_types.append('dependencies')
            else:
                file_types.append('files')
        
        unique_types = list(set(file_types))
        if len(unique_types) == 1:
            return f"chore: update {unique_types[0]}"
        return f"chore: update {', '.join(unique_types[:2])}"
    
    def analyze_file_changes(self, file_path):
        """Analyze changes in a file"""
        try:
            diff_output = subprocess.check_output(
                ['git', 'diff', 'HEAD', file_path],
                encoding='utf-8',
                stderr=subprocess.DEVNULL
            )
            
            changes = {
                'additions': 0,
                'deletions': 0,
                'functions': [],
                'classes': []
            }
            
            for line in diff_output.split('\n'):
                if line.startswith('+') and not line.startswith('+++'):
                    changes['additions'] += 1
                    
                    # Detect new functions
                    if 'def ' in line:
                        match = re.search(r'def\s+(\w+)', line)
                        if match:
                            changes['functions'].append(match.group(1))
                    
                    # Detect new classes
                    if 'class ' in line:
                        match = re.search(r'class\s+(\w+)', line)
                        if match:
                            changes['classes'].append(match.group(1))
                
                elif line.startswith('-') and not line.startswith('---'):
                    changes['deletions'] += 1
            
            return changes
            
        except subprocess.CalledProcessError:
            return None
    
    def generate_changelog(self):
        """Generate changelog file"""
        print("🔍 Analyzing git commits and changes...")
        
        # Get commits
        commits = self.get_commits_today()
        
        # Get unstaged changes
        unstaged = self.get_unstaged_changes()
        if unstaged:
            commits.append(unstaged)
        
        if not commits:
            print("ℹ️  No changes found for today")
            return
        
        # Categorize commits
        categorized = defaultdict(list)
        for commit in commits:
            category = self.categorize_commit(commit)
            categorized[category].append(commit)
        
        # Generate changelog content
        today = datetime.now().strftime('%Y-%m-%d')
        changelog_file = self.docs_dir / f"codeChange-{datetime.now().strftime('%Y%m%d')}.md"
        
        content = self.build_changelog_content(today, categorized, commits)
        
        # Write changelog
        with open(changelog_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Changelog generated: {changelog_file}")
        print(f"📊 Total commits: {len(commits)}")
        print(f"📁 Categories: {len(categorized)}")
        
        return changelog_file
    
    def build_changelog_content(self, date, categorized, commits):
        """Build changelog markdown content"""
        content = f"# Code Changes - {date}\n\n"
        content += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        content += "---\n\n"
        
        # Summary
        content += "## 📊 Summary\n\n"
        content += f"- **Total Changes**: {len(commits)}\n"
        content += f"- **Categories**: {len(categorized)}\n"
        
        total_files = sum(len(c['files']) for c in commits)
        content += f"- **Files Modified**: {total_files}\n\n"
        
        # Changes by category
        for category in self.categories.keys():
            if category in categorized and categorized[category]:
                content += f"## {category}\n\n"
                
                for commit in categorized[category]:
                    # Commit info
                    if commit['hash'] == 'UNSTAGED':
                        content += f"### 🔄 Unstaged Changes\n\n"
                    else:
                        content += f"### {commit['message']}\n\n"
                        content += f"**Commit**: `{commit['hash'][:7]}`  \n"
                        content += f"**Date**: {commit['date']}\n\n"
                    
                    # Files changed
                    if commit['files']:
                        content += "**Files**:\n"
                        for file in commit['files'][:10]:  # Limit to 10 files
                            content += f"- `{file}`\n"
                        
                        if len(commit['files']) > 10:
                            content += f"- ... and {len(commit['files']) - 10} more files\n"
                        
                        content += "\n"
                    
                    # Analyze changes for Python files
                    py_files = [f for f in commit['files'] if f.endswith('.py')]
                    if py_files and commit['hash'] != 'UNSTAGED':
                        for py_file in py_files[:3]:  # Analyze first 3 Python files
                            changes = self.analyze_file_changes(py_file)
                            if changes and (changes['functions'] or changes['classes']):
                                content += f"**Changes in `{py_file}`**:\n"
                                if changes['functions']:
                                    content += f"- New functions: {', '.join(changes['functions'][:5])}\n"
                                if changes['classes']:
                                    content += f"- New classes: {', '.join(changes['classes'][:5])}\n"
                                content += "\n"
                    
                    content += "---\n\n"
        
        # Footer
        content += "## 📝 Notes\n\n"
        content += "This changelog was automatically generated from git commits and file changes.\n"
        content += "For more details, check the git log or individual commit diffs.\n"
        
        return content


def main():
    """Main entry point"""
    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("=" * 60)
    print("WACSA-MD2 UI Changelog Generator")
    print("=" * 60)
    print()
    
    try:
        generator = ChangelogGenerator()
        changelog_file = generator.generate_changelog()
        
        if changelog_file:
            print()
            print("=" * 60)
            print("✅ Changelog generation completed!")
            print("=" * 60)
            print()
            print("Next steps:")
            print(f"1. Review: {changelog_file}")
            print(f"2. Stage: git add {changelog_file}")
            print("3. Commit: git commit -m 'docs: add daily changelog'")
            print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
