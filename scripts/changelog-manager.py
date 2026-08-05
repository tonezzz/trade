#!/usr/bin/env python3
"""
CHANGELOG Management Script
Advanced changelog management including version releases and validation
"""

import re
import sys
import argparse
from datetime import date
from pathlib import Path


class ChangelogManager:
    def __init__(self, changelog_path="CHANGELOG.md"):
        self.changelog_path = Path(changelog_path)
        if not self.changelog_path.exists():
            raise FileNotFoundError(f"CHANGELOG.md not found at {changelog_path}")
        
        self.content = self.changelog_path.read_text()
        self.sections = self._parse_sections()
    
    def _parse_sections(self):
        """Parse changelog into sections"""
        sections = {}
        current_section = None
        current_content = []
        
        for line in self.content.split('\n'):
            section_match = re.match(r'^## \[([^\]]+)\]', line)
            if section_match:
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = section_match.group(1)
                current_content = [line]
            else:
                if current_section:
                    current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def add_entry(self, change_type, description, unreleased_only=True):
        """Add an entry to the changelog"""
        change_type = change_type.lower()
        valid_types = ['added', 'changed', 'deprecated', 'removed', 'fixed', 'security']
        
        if change_type not in valid_types:
            raise ValueError(f"Invalid change type. Must be one of: {', '.join(valid_types)}")
        
        if 'Unreleased' not in self.sections:
            raise ValueError("[Unreleased] section not found in CHANGELOG.md")
        
        # Update the Unreleased section
        unreleased_content = self.sections['Unreleased']
        subsection = f"### {change_type.capitalize()}"
        
        if subsection in unreleased_content:
            # Add to existing subsection
            pattern = rf'({re.escape(subsection)}\n)'
            replacement = rf'\1- {description}\n'
            unreleased_content = re.sub(pattern, replacement, unreleased_content, count=1)
        else:
            # Add new subsection
            unreleased_content = unreleased_content.replace(
                "## [Unreleased]",
                f"## [Unreleased]\n\n{subsection}\n- {description}"
            )
        
        self.sections['Unreleased'] = unreleased_content
        self._save_changes()
        print(f"✅ Added [{change_type}] {description}")
    
    def release_version(self, version, release_date=None):
        """Create a new release from Unreleased entries"""
        if 'Unreleased' not in self.sections:
            raise ValueError("[Unreleased] section not found in CHANGELOG.md")
        
        if release_date is None:
            release_date = date.today().isoformat()
        
        unreleased_content = self.sections['Unreleased']
        
        # Check if there are any entries in Unreleased
        if not re.search(r'### (Added|Changed|Deprecated|Removed|Fixed|Security)', unreleased_content):
            print("⚠️  No entries in [Unreleased] section. Nothing to release.")
            return
        
        # Create new version section
        new_version = f"## [{version}] - {release_date}\n\n{unreleased_content.split('## [Unreleased]')[1].strip()}"
        
        # Update Unreleased to be empty
        new_unreleased = "## [Unreleased]\n\n### Added\n\n### Changed\n\n### Deprecated\n\n### Removed\n\n### Fixed\n\n### Security"
        
        # Rebuild content
        new_content = []
        version_added = False
        
        for section_name, section_content in self.sections.items():
            if section_name == 'Unreleased':
                new_content.append(new_unreleased)
                if not version_added:
                    new_content.append("\n\n" + new_version)
                    version_added = True
            else:
                new_content.append(section_content)
        
        self.content = '\n\n'.join(new_content)
        self._save_changes()
        print(f"✅ Released version {version} on {release_date}")
    
    def validate(self):
        """Validate changelog format and structure"""
        issues = []
        
        # Check for required sections
        if 'Unreleased' not in self.sections:
            issues.append("Missing [Unreleased] section")
        
        # Check for standard subsections in Unreleased
        if 'Unreleased' in self.sections:
            required_subsections = ['Added', 'Changed', 'Deprecated', 'Removed', 'Fixed', 'Security']
            for subsection in required_subsections:
                if f"### {subsection}" not in self.sections['Unreleased']:
                    issues.append(f"Missing '### {subsection}' in [Unreleased]")
        
        # Check version format
        for section_name in self.sections:
            if section_name != 'Unreleased':
                if not re.match(r'^\d+\.\d+\.\d+', section_name):
                    issues.append(f"Invalid version format: {section_name}")
        
        if issues:
            print("❌ Validation failed:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print("✅ CHANGELOG.md is valid")
            return True
    
    def _save_changes(self):
        """Save changes to changelog file"""
        # Rebuild content from sections
        new_content = []
        for section_name, section_content in self.sections.items():
            new_content.append(section_content)
        
        self.content = '\n\n'.join(new_content)
        self.changelog_path.write_text(self.content)


def main():
    parser = argparse.ArgumentParser(description="CHANGELOG Management Script")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add entry command
    add_parser = subparsers.add_parser('add', help='Add an entry to the changelog')
    add_parser.add_argument('type', choices=['added', 'changed', 'deprecated', 'removed', 'fixed', 'security'],
                           help='Type of change')
    add_parser.add_argument('description', help='Description of the change')
    
    # Release command
    release_parser = subparsers.add_parser('release', help='Release a new version')
    release_parser.add_argument('version', help='Version number (e.g., 1.2.3)')
    release_parser.add_argument('--date', help='Release date (default: today)')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate changelog format')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        manager = ChangelogManager()
        
        if args.command == 'add':
            manager.add_entry(args.type, args.description)
        elif args.command == 'release':
            manager.release_version(args.version, args.date)
        elif args.command == 'validate':
            manager.validate()
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
