#!/usr/bin/env python3
"""Fix v2: insert brand sections INSIDE cat-block, after diff-box"""
import re

# (brands dict same as before - omitted for brevity, will import from fix_brands)
exec(open("/home/ubuntu/ich-diy-research/fix_brands.py").read().split("# Read file")[0])

# Read file
with open("/home/ubuntu/ich-diy-research/competitor-research.html", "r") as f:
    html = f.read()

# Find all diff-box closes. Pattern: after each category's diff-box, before cat-block close.
# diff-box closes with:     </div>  (4-space indent)
# cat-block closes with:   </div>    (2-space indent)
# Insert AFTER diff-box close, BEFORE cat-block close

markers = [
    ("<!-- CATEGORY 2: TIE-DYE -->", "c1"),
    ("<!-- CATEGORY 3: RONGHUA / CHANHUA -->", "c2"),
    ("<!-- CATEGORY 4: SACHET -->", "c3"),
    ("<!-- CATEGORY 5: POTTERY -->", "c4"),
    ("<!-- CATEGORY 6: KNOT -->", "c5"),
    ("<!-- CATEGORY 7: PAPER / PRINT -->", "c6"),
    ("<!-- CATEGORY 8: PAPER CUT -->", "c7"),
    ("<!-- MASTER SUMMARY -->", "c8"),
]

# For c1 specifically, look backwards from c2's position
# Find where the cat-block before c2 ends

insertions = []
for marker, cat_key in markers:
    pos = html.find(marker)
    if pos < 0:
        print(f"❌ {cat_key}: marker not found")
        continue
    
    before = html[:pos]
    
    # Find the last occurrence of diff-box close before this marker
    # Pattern: '    </div>\n  </div>' where:
    #   '    </div>' = diff-box close  
    #   '  </div>'   = cat-block close
    pattern = '    </div>\n  </div>'
    last_idx = before.rfind(pattern)
    
    if last_idx < 0:
        # Try alternate pattern for c1 (might have different structure)
        pattern2 = '</div>\n  </div>'
        last_idx = before.rfind(pattern2)
        if last_idx >= 0:
            # Find the actual diff-box close </div> within this
            insert_pos = before.rfind('</div>', 0, last_idx + 6)
            if insert_pos >= 0:
                insert_pos += len('</div>')
            else:
                insert_pos = last_idx + len('</div>\n')
        else:
            print(f"❌ {cat_key}: no pattern match")
            continue
    else:
        # Insert right after diff-box close: '    </div>'
        insert_pos = last_idx + len('    </div>')
    
    brand_html = make_brand_section(cat_key)
    insertions.append((insert_pos, brand_html, cat_key))

# Apply in reverse order
insertions.sort(key=lambda x: x[0], reverse=True)
for pos, brand_html, cat_key in insertions:
    html = html[:pos] + "\n" + brand_html + html[pos:]
    print(f"✅ {cat_key}: inserted at {pos}")

with open("/home/ubuntu/ich-diy-research/competitor-research.html", "w") as f:
    f.write(html)

print(f"\n✅ Done! {len(html)} bytes")
