#!/usr/bin/env node

/* eslint-env node */
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

/*
USAGE NOTES:
- Run 'npm run changelog' BEFORE staging files
- After generating changelog, stage the new changelog file:
  git add custom/docs/changelog/daily/codeChange-$(date +%Y%m%d).md
- Then commit and push
- This ensures changelog changes are included in the same commit
*/

class DynamicChangelogGenerator {
    constructor() {
        this.docsDir = path.join(process.cwd(), 'custom/docs/changelog/daily');
        this.patterns = this.initializePatterns();
        this.categories = this.initializeCategories();
    }

    initializePatterns() {
        return {
            functionKeywords: {
                'whatsapp': 'WhatsApp functionality',
                'message': 'Message handling',
                'send': 'Message sending',
                'receive': 'Message receiving',
                'media': 'Media handling',
                'text': 'Text message',
                'file': 'File operations',
                'api': 'API integration',
                'client': 'API client',
                'ui': 'UI components',
                'button': 'Button functionality',
                'entry': 'Input field',
                'radio': 'Radio button',
                'browse': 'File browsing',
                'upload': 'File upload',
                'status': 'Status management',
                'connection': 'Connection handling',
                'server': 'Server communication',
                'endpoint': 'API endpoint',
                'request': 'HTTP request',
                'response': 'Response handling',
                'error': 'Error handling',
                'validation': 'Input validation',
                'format': 'Data formatting',
                'parse': 'Data parsing',
                'config': 'Configuration',
                'settings': 'Settings management',
                'build': 'Build process',
                'executable': 'Executable creation',
                'package': 'Packaging'
            },
            changeKeywords: {
                '+import': 'Add import',
                '+def': 'Add function',
                '+class': 'Add class',
                '+var': 'Add variable',
                '+const': 'Add constant',
                'return': 'Add return logic',
                'try': 'Add error handling',
                'except': 'Add exception handling',
                'if': 'Add conditional logic',
                'for': 'Add loop',
                'while': 'Add loop',
                'ctk.': 'Add CustomTkinter component',
                'tk.': 'Add Tkinter component',
                'requests': 'Add HTTP request',
                'json': 'Add JSON handling',
                'datetime': 'Add date/time handling',
                'pathlib': 'Add path handling',
                'messagebox': 'Add message dialog',
                'filedialog': 'Add file dialog'
            }
        };
    }

    initializeCategories() {
        return {
            '✨ Features': [],
            '🐞 Fixes': [],
            '📖 Documentation': [],
            '🧪 Tests': [],
            '🎨 UI/UX': [],
            '🔌 API': [],
            '⚙️ Config': [],
            '📦 Build': [],
            '⚙️ Others': []
        };
    }

    categorizeCommit(commit) {
        const { message, files } = commit;
        
        // Priority-based categorization
        if (message.startsWith('feat:') || message.includes('add') || message.includes('new')) {
            return '✨ Features';
        }
        
        if (message.startsWith('fix:') || message.includes('fix') || message.includes('bug')) {
            return '🐞 Fixes';
        }
        
        if (files.some(file => file.includes('.md') || file.includes('docs/') || file.includes('README'))) {
            return '📖 Documentation';
        }
        
        if (files.some(file => file.includes('.test') || file.includes('spec') || file.includes('test'))) {
            return '🧪 Tests';
        }
        
        if (files.some(file => file.includes('.py') && (file.includes('main.py') || file.includes('ui') || file.includes('gui')))) {
            return '🎨 UI/UX';
        }
        
        if (files.some(file => file.includes('api') || file.includes('client') || message.includes('api'))) {
            return '🔌 API';
        }
        
        if (files.some(file => file.includes('build') || file.includes('requirements') || file.includes('setup'))) {
            return '📦 Build';
        }
        
        if (files.some(file => file.includes('.env') || file.includes('config') || file.includes('Config'))) {
            return '⚙️ Config';
        }
        
        if (message.startsWith('refactor:') || message.startsWith('chore:') || 
            message.includes('update') || message.includes('refactor')) {
            return '⚙️ Others';
        }
        
        return '⚙️ Others';
    }

    getCommitsSinceLastRun() {
        try {
            const commits = [];
            
            // First, get today's commits
            const today = new Date().toISOString().split('T')[0];
            const gitCommand = `git log --since="${today} 00:00:00" --until="${today} 23:59:59" --pretty=format:"%H|%s|%ai" --name-only`;
            const output = execSync(gitCommand, { encoding: 'utf8' });
            
            const lines = output.split('\n');
            let currentCommit = null;
            
            lines.forEach((line) => {
                if (line.includes('|')) {
                    if (currentCommit) {
                        commits.push(currentCommit);
                    }
                    const [hash, message, date] = line.split('|');
                    currentCommit = {
                        hash: hash.trim(),
                        message: message.trim(),
                        date: date.trim(),
                        files: []
                    };
                } else if (line.trim() && currentCommit) {
                    currentCommit.files.push(line.trim());
                }
            });
            
            if (currentCommit) {
                commits.push(currentCommit);
            }
            
            // Then, check for unstaged changes
            try {
                const statusOutput = execSync('git status --porcelain', { encoding: 'utf8' });
                const changedFiles = statusOutput.split('\n')
                    .filter(line => line.trim())
                    .map(line => line.substring(3).trim()); // Remove status prefix
                
                if (changedFiles.length > 0) {
                    // Create a virtual commit for unstaged changes
                    const unstagedCommit = {
                        hash: 'UNSTAGED',
                        message: this.generateUnstagedMessage(changedFiles),
                        date: new Date().toISOString(),
                        files: changedFiles
                    };
                    commits.push(unstagedCommit);
                }
            } catch (statusError) {
                // Ignore status errors
            }
            
            return commits;
        } catch (error) {
            console.warn('No commits found for today or git command failed:', error.message);
            return [];
        }
    }

    generateUnstagedMessage(files) {
        const fileTypes = files.map(file => {
            if (file.includes('main.py')) return 'main UI';
            if (file.includes('api_client.py')) return 'API client';
            if (file.includes('build.py')) return 'build script';
            if (file.includes('.py')) return 'python code';
            if (file.includes('.md')) return 'docs';
            if (file.includes('requirements.txt')) return 'dependencies';
            return 'files';
        });
        
        const uniqueTypes = [...new Set(fileTypes)];
        if (uniqueTypes.length === 1) {
            return `chore: update ${uniqueTypes[0]}`;
        }
        return `chore: update ${uniqueTypes.join(', ')}`;
    }

    getFileDiff(filePath, commitHash) {
        try {
            if (commitHash === 'UNSTAGED') {
                // For unstaged changes, get diff against HEAD
                const gitCommand = `git diff HEAD -- ${filePath}`;
                const output = execSync(gitCommand, { encoding: 'utf8' });
                return output;
            } else {
                const gitCommand = `git show ${commitHash} -- ${filePath}`;
                const output = execSync(gitCommand, { encoding: 'utf8' });
                return output;
            }
        } catch (error) {
            return '';
        }
    }

    extractLineNumbers(diff) {
        const lineNumbers = [];
        const lines = diff.split('\n');
        let currentLine = 0;
        
        lines.forEach((line) => {
            if (line.startsWith('@@')) {
                const match = line.match(/@@ -\d+(?:,\d+)?\s+\+(\d+)(?:,\d+)?\s+@@/);
                if (match) {
                    currentLine = parseInt(match[1]);
                } else {
                    const altMatch = line.match(/@@ -\d+(?:,\d+)?\s+\+(\d+)/);
                    if (altMatch) {
                        currentLine = parseInt(altMatch[1]);
                    }
                }
            } else if (line.startsWith('+') && !line.startsWith('+++')) {
                if (!isNaN(currentLine) && currentLine > 0) {
                    lineNumbers.push(currentLine);
                    currentLine++;
                }
            } else if (line.startsWith('-') && !line.startsWith('---')) {
                // Removed line, don't increment
            } else if (!line.startsWith('@@') && !line.startsWith('---') && !line.startsWith('+++') && !line.startsWith('index') && !line.startsWith('diff')) {
                if (!isNaN(currentLine) && currentLine > 0) {
                    currentLine++;
                }
            }
        });
        
        if (lineNumbers.length === 0) return 'N/A';
        
        if (lineNumbers.length === 1) return `${lineNumbers[0]}`;
        
        const ranges = [];
        let start = lineNumbers[0];
        let end = lineNumbers[0];
        
        for (let i = 1; i < lineNumbers.length; i++) {
            if (lineNumbers[i] === end + 1) {
                end = lineNumbers[i];
            } else {
                ranges.push(start === end ? start : `${start}-${end}`);
                start = lineNumbers[i];
                end = lineNumbers[i];
            }
        }
        ranges.push(start === end ? start : `${start}-${end}`);
        
        return ranges.join(', ');
    }

    extractFunction(message, diff) {
        // Strategy 1: Extract from commit message
        if (message.includes(':')) {
            const afterColon = message.split(':')[1];
            if (afterColon && afterColon.trim().length > 5) {
                return afterColon.trim();
            }
        }
        
        // Strategy 2: Extract from file context
        const fileName = path.basename('unknown');
        if (fileName.includes('main')) return 'Main UI functionality';
        if (fileName.includes('api_client')) return 'API client implementation';
        if (fileName.includes('build')) return 'Build configuration';
        
        // Strategy 3: Extract from diff content
        for (const [keyword, description] of Object.entries(this.patterns.functionKeywords)) {
            if (message.toLowerCase().includes(keyword) || diff.toLowerCase().includes(keyword)) {
                return description;
            }
        }
        
        // Strategy 4: Extract from code patterns
        if (diff.includes('def ') || diff.includes('class ')) {
            return 'Function/class implementation';
        }
        if (diff.includes('import ')) {
            return 'Import dependency';
        }
        
        return 'Code implementation';
    }

    extractChanges(diff) {
        const changes = [];
        const lines = diff.split('\n');
        
        lines.forEach((line) => {
            if (line.startsWith('+') && !line.startsWith('+++')) {
                const codeLine = line.substring(1);
                
                // Check for specific patterns
                for (const [pattern, description] of Object.entries(this.patterns.changeKeywords)) {
                    if (codeLine.includes(pattern.replace('+', ''))) {
                        changes.push(description);
                        break;
                    }
                }
                
                // Additional pattern matching for Python
                if (codeLine.includes('def ') && codeLine.includes('()')) {
                    changes.push('Add function');
                }
                if (codeLine.includes('ctk.CTk')) {
                    changes.push('Add CustomTkinter component');
                }
                if (codeLine.includes('self.')) {
                    changes.push('Add class method');
                }
                if (codeLine.includes('requests.')) {
                    changes.push('Add HTTP request');
                }
            }
            
            if (line.startsWith('-') && !line.startsWith('---')) {
                const codeLine = line.substring(1);
                if (codeLine.includes('print(') || codeLine.includes('console.log')) {
                    changes.push('Remove debug logs');
                }
            }
        });
        
        // Remove duplicates and join
        const uniqueChanges = [...new Set(changes)];
        return uniqueChanges.length > 0 ? uniqueChanges.join(', ') : 'Code implementation';
    }

    formatTimestamp(date) {
        const d = new Date(date);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const hours = String(d.getHours()).padStart(2, '0');
        const minutes = String(d.getMinutes()).padStart(2, '0');
        const seconds = String(d.getSeconds()).padStart(2, '0');
        
        return `${year}${month}${day}_${hours}${minutes}${seconds}`;
    }

    formatCodeDiff(diff) {
        if (!diff || diff.length < 10) return '# No significant code changes';
        
        const lines = diff.split('\n');
        const formattedLines = [];
        let lineCounter = 0;
        let inDiffBlock = false;
        let hasChanges = false;
        let blockStartLine = 0;
        
        lines.forEach((line) => {
            if (line.startsWith('@@')) {
                const match = line.match(/@@ -\d+(?:,\d+)?\s+\+(\d+)/);
                if (match) {
                    blockStartLine = parseInt(match[1]);
                    lineCounter = blockStartLine;
                    inDiffBlock = true;
                    formattedLines.push(`# Line ${lineCounter}:`);
                }
            } else if (line.startsWith('+') && !line.startsWith('+++')) {
                if (inDiffBlock && !isNaN(lineCounter) && lineCounter > 0) {
                    formattedLines.push(`+ ${line.substring(1)}`);
                    lineCounter++;
                    hasChanges = true;
                }
            } else if (line.startsWith('-') && !line.startsWith('---')) {
                if (inDiffBlock) {
                    if (!isNaN(lineCounter) && lineCounter > 0) {
                        formattedLines.push(`- ${line.substring(1)}`);
                    } else {
                        formattedLines.push(`- ${line.substring(1)}`);
                    }
                    hasChanges = true;
                }
            } else if (line.startsWith(' ')) {
                if (inDiffBlock && !isNaN(lineCounter) && lineCounter > 0) {
                    lineCounter++;
                }
            }
        });
        
        // If no changes found, return minimal message
        if (!hasChanges) {
            return '# No significant changes detected';
        }
        
        // For very small diffs, show all
        if (formattedLines.length <= 10) {
            return formattedLines.join('\n');
        }
        
        // Limit output to prevent huge diffs
        if (formattedLines.length > 50) {
            formattedLines.splice(25, formattedLines.length - 50, '  # ... (truncated for brevity)');
        }
        
        return formattedLines.join('\n');
    }

    generateChangelog() {
        const commits = this.getCommitsSinceLastRun();
        
        if (commits.length === 0) {
            console.log('No commits found for today');
            return;
        }
        
        const categories = this.initializeCategories();
        const processedFiles = new Set();
        
        commits.forEach(commit => {
            const category = this.categorizeCommit(commit);
            const timestamp = this.formatTimestamp(commit.date);
            
            commit.files.forEach(filePath => {
                // Skip if already processed this file with same commit hash
                const fileKey = `${filePath}-${commit.hash}`;
                if (processedFiles.has(fileKey)) return;
                processedFiles.add(fileKey);
                
                const diff = this.getFileDiff(filePath, commit.hash);
                const lineNumbers = this.extractLineNumbers(diff);
                const fungsi = this.extractFunction(commit.message, diff);
                const perubahan = this.extractChanges(diff);
                const formattedDiff = this.formatCodeDiff(diff);
                
                const entry = {
                    file: filePath,
                    timestamp: timestamp,
                    fungsi: fungsi,
                    perubahan: perubahan,
                    lines: lineNumbers,
                    diff: formattedDiff,
                    commit: commit
                };
                
                categories[category].push(entry);
            });
        });
        
        return this.formatMarkdown(categories);
    }

    formatMarkdown(categories) {
        const today = new Date();
        const dateStr = today.toLocaleDateString('id-ID', { 
            day: 'numeric', 
            month: 'long', 
            year: 'numeric' 
        });
        
        let markdown = `# Code Changes Summary\n\n## ${dateStr}\n\n`;
        
        let totalFiles = 0;
        const categoryCounts = {};
        
        Object.entries(categories).forEach(([category, entries]) => {
            if (entries.length === 0) return;
            
            totalFiles += entries.length;
            categoryCounts[category] = entries.length;
            
            markdown += `### ${category}\n\n`;
            
            entries.forEach((entry, index) => {
                markdown += `#### ${index + 1}. ${entry.file} [${entry.timestamp}]\n`;
                markdown += `**Fungsi:** ${entry.fungsi}  \n`;
                markdown += `**Perubahan:** ${entry.perubahan}  \n`;
                if (entry.lines !== 'N/A') {
                    markdown += `**Lines:** ${entry.lines}\n`;
                }
                
                if (entry.diff && entry.diff !== '# No significant code changes') {
                    markdown += '\n```python\n';
                    markdown += entry.diff;
                    markdown += '\n```\n';
                }
                
                markdown += '\n---\n\n';
            });
        });
        
        // Add summary
        markdown += '## 📊 **Summary**\n';
        Object.entries(categoryCounts).forEach(([category, count]) => {
            markdown += `- **${category}:** ${count} item${count > 1 ? 's' : ''}\n`;
        });
        markdown += `- **Total Files Modified:** ${totalFiles}\n`;
        
        // Determine main focus
        const mainCategory = Object.entries(categoryCounts)
            .sort(([,a], [,b]) => b - a)[0];
        if (mainCategory) {
            markdown += `- **Main Focus:** ${mainCategory[0].replace(/[\u2700-\u27BF]\s/, '')}\n`;
        }
        
        return markdown;
    }

    saveChangelog(content) {
        // Ensure directory exists
        if (!fs.existsSync(this.docsDir)) {
            fs.mkdirSync(this.docsDir, { recursive: true });
        }
        
        const today = new Date();
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, '0');
        const day = String(today.getDate()).padStart(2, '0');
        
        const filename = `codeChange-${year}${month}${day}.md`;
        const filepath = path.join(this.docsDir, filename);
        
        // Always overwrite the file with fresh content
        fs.writeFileSync(filepath, content);
        
        console.log(`Changelog saved to: ${filepath}`);
        return filepath;
    }

    run() {
        try {
            console.log('Generating changelog...');
            const changelog = this.generateChangelog();
            
            if (changelog) {
                const filepath = this.saveChangelog(changelog);
                console.log('✅ Changelog generated successfully!');
                console.log(`📁 File: ${filepath}`);
            } else {
                console.log('ℹ️ No changes to document today');
            }
        } catch (error) {
            console.error('❌ Error generating changelog:', error.message);
            process.exit(1);
        }
    }
}

// Run if called directly
if (require.main === module) {
    const generator = new DynamicChangelogGenerator();
    generator.run();
}

module.exports = DynamicChangelogGenerator;
