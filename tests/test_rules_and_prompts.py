import os
import yaml
from pathlib import Path

def test_rules_have_valid_frontmatter():
    project_root = Path(__file__).resolve().parent.parent
    rules_dir = project_root / ".agents" / "rules"
    
    assert rules_dir.exists(), "Rules directory does not exist"
    
    rule_files = list(rules_dir.glob("*.md"))
    assert len(rule_files) > 0, "No rule files found"
    
    for rule_file in rule_files:
        with open(rule_file, "r") as f:
            content = f.read()
        
        # Extract frontmatter
        assert content.startswith("---"), f"{rule_file.name} does not start with ---"
        end_idx = content.find("---", 3)
        assert end_idx != -1, f"{rule_file.name} does not have a closing ---"
        
        frontmatter_content = content[3:end_idx].strip()
        try:
            frontmatter = yaml.safe_load(frontmatter_content)
        except yaml.YAMLError as e:
            assert False, f"Failed to parse YAML frontmatter in {rule_file.name}: {e}"
        
        assert isinstance(frontmatter, dict), f"Frontmatter in {rule_file.name} is not a dictionary"
        assert "name" in frontmatter, f"Missing 'name' in frontmatter of {rule_file.name}"
        assert "description" in frontmatter, f"Missing 'description' in frontmatter of {rule_file.name}"

def test_prompt_wrappers_resolve_correctly():
    project_root = Path(__file__).resolve().parent.parent
    prompts_dir = project_root / ".agents" / "prompts"
    skill_commands_dir = project_root / ".agents" / "skill_commands"
    claude_skills_dir = project_root / ".claude" / "skills"
    gemini_commands_dir = project_root / ".gemini" / "commands"
    
    assert prompts_dir.exists(), "Prompts directory does not exist"
    
    prompt_files = list(prompts_dir.glob("*.md"))
    assert len(prompt_files) > 0, "No prompt files found"
    
    for prompt_file in prompt_files:
        if prompt_file.name == "README.md":
            continue
            
        name = prompt_file.stem
        
        # 1. Check .agents/skill_commands/<name>/SKILL.md
        skill_command_dir = skill_commands_dir / name
        skill_command_file = skill_command_dir / "SKILL.md"
        assert skill_command_file.exists(), f"Missing wrapper {skill_command_file}"
        
        with open(skill_command_file, "r") as f:
            content = f.read()
        expected_pointer = f"@.agents/prompts/{name}.md"
        assert expected_pointer in content, f"{skill_command_file} does not contain {expected_pointer}"
        
        # 2. Check .claude/skills/<name>
        claude_link = claude_skills_dir / name
        assert claude_link.is_symlink(), f"{claude_link} is missing or not a symlink"
        
        target = os.readlink(claude_link)
        expected_target = f"../../.agents/skill_commands/{name}"
        assert target == expected_target, f"{claude_link} points to {target}, expected {expected_target}"
        
        # 3. Check .gemini/commands/<name>.toml
        gemini_file = gemini_commands_dir / f"{name}.toml"
        assert gemini_file.exists(), f"Missing Gemini wrapper {gemini_file}"
        
        with open(gemini_file, "r") as f:
            gemini_content = f.read()
        
        assert f".agents/prompts/{name}.md" in gemini_content, f"{gemini_file} does not point to the canonical prompt"

