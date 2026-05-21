import re
import sys
import os

def compile_ojs_blocks(ojs_blocks):
    """
    Parses and translates OJS blocks into a single reactive HTML/JS widget.
    """
    cleaned_blocks = []
    for block in ojs_blocks:
        lines = [line for line in block.splitlines() if not line.strip().startswith('//|')]
        cleaned_blocks.append('\n'.join(lines))
        
    all_content = '\n'.join(cleaned_blocks)
    
    # 1. Match Inputs.select
    select_match = re.search(
        r'viewof\s+(\w+)\s*=\s*Inputs\.select\(\s*(\[[^\]]+\])\s*,\s*\{\s*value:\s*([^,]+),\s*label:\s*([^}]+)\s*\}\)',
        all_content
    )
    
    if not select_match:
        return None
        
    var_name = select_match.group(1)
    options = eval(select_match.group(2))
    default_val = select_match.group(3).strip().strip('"').strip("'")
    label = select_match.group(4).strip().strip('"').strip("'")
    
    # Build HTML select dropdown
    options_html = '\n'.join(
        f'      <option value="{opt}"{" selected" if opt == default_val else ""}>{opt}</option>'
        for opt in options
    )
    
    html_input = f"""<div style="background: #f8fafc; padding: 1.5rem; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 1.5rem;">
  <div style="margin-bottom: 1rem; font-family: sans-serif;">
    <label for="{var_name}-select" style="font-weight: 600; margin-right: 0.5rem; color: #1e293b;">{label}</label>
    <select id="{var_name}-select" style="padding: 0.5rem; border-radius: 4px; border: 1px solid #cbd5e1; background: white; color: #1e293b;">
{options_html}
    </select>
  </div>
  <div id="dynamic-chart" style="width:100%; height:400px; background: white; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);"></div>
</div>"""

    # 2. Extract Data Array
    data_match = re.search(r'data\s*=\s*(\[.*?\])', all_content, re.DOTALL)
    data_json = data_match.group(1) if data_match else "[]"
    
    # 3. Clean and Extract Reactive JS Code
    clean_js = all_content
    # Remove viewof statement
    clean_js = re.sub(r'viewof\s+\w+\s*=\s*Inputs\.select\(.*?\)', '', clean_js, flags=re.DOTALL)
    # Remove data = [...] statement
    clean_js = re.sub(r'data\s*=\s*\[.*?\]', '', clean_js, flags=re.DOTALL)
    
    # Prefix variable declarations with const
    lines = []
    for line in clean_js.splitlines():
        match = re.match(r'^(\s*)([a-zA-Z_]\w*)\s*=\s*(?!==|=>)(.*)', line)
        if match:
            indent, var, rest = match.groups()
            lines.append(f"{indent}const {var} = {rest}")
        else:
            lines.append(line)
            
    clean_js = '\n'.join(lines)
    clean_js = clean_js.replace(var_name, 'category')
    
    # Indent the reactive code for updatePlot
    reactive_code = '\n'.join('      ' + line for line in clean_js.splitlines() if line.strip())
    
    js_code = f"""
<script type="text/javascript">
  document.addEventListener("DOMContentLoaded", function() {{
    const data = {data_json};

    function updatePlot(category) {{
      if (typeof Plotly === 'undefined') {{
        console.error("Plotly is not loaded");
        return;
      }}
{reactive_code}
    }}

    const select = document.getElementById("{var_name}-select");
    if (select) {{
      select.addEventListener("change", function(e) {{
        updatePlot(e.target.value);
      }});
      updatePlot(select.value);
    }}
  }});
</script>
"""
    plotly_script = '<script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>'
    return plotly_script + "\n" + html_input + "\n" + js_code

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 compile_ojs_in_markdown.py <path_to_markdown>")
        sys.exit(1)
        
    md_path = sys.argv[1]
    if not os.path.exists(md_path):
        print(f"Rapport GFM non encore généré : {md_path}. Saut de la compilation OJS.")
        sys.exit(0)
        
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Regex to find:
    # ``` {ojs} or ```{ojs} blocks
    pattern = re.compile(r'```\s*\{\s*ojs\s*\}\n(.*?)\n```', re.DOTALL)
    ojs_blocks = pattern.findall(content)
    
    if not ojs_blocks:
        print("No OJS blocks found in the markdown.")
        sys.exit(0)
        
    compiled_widget = compile_ojs_blocks(ojs_blocks)
    
    if compiled_widget:
        # 1. Translate echoed OJS blocks to standard JS codeblocks, and remove hidden ones
        def replace_block(match):
            block_content = match.group(1)
            if 'echo: false' in block_content:
                return ''
            
            clean_lines = [line for line in block_content.splitlines() if not line.strip().startswith('//|')]
            clean_code = '\n'.join(clean_lines)
            return f"```javascript\n{clean_code}\n```"

        content = pattern.sub(replace_block, content)
        
        # 2. Replace the <div id="dynamic-chart"...> element with the compiled interactive widget
        div_pattern = re.compile(r'<div\s+id="dynamic-chart".*?>\s*</div>', re.DOTALL)
        content = div_pattern.sub(compiled_widget, content)
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully compiled OJS blocks into HTML/JS in {md_path}!")
    else:
        print("Failed to compile OJS blocks.")

if __name__ == '__main__':
    main()
