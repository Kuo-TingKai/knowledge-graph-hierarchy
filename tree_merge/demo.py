class TreeNode:
    def __init__(self, val=""):
        self.val = val
        self.children = []

def create_tree1():
    # Tree 1: 以治療方式為主的分類
    root = TreeNode("醫學美容")
    
    # Level 1
    non_surgical = TreeNode("非侵入性治療")
    surgical = TreeNode("侵入性治療")
    root.children = [non_surgical, surgical]
    
    # Level 2 - 非侵入性治療的子項目
    laser = TreeNode("雷射治療")
    injection = TreeNode("注射治療")
    non_surgical.children = [laser, injection]
    
    # Level 3 - 雷射治療的子項目
    laser.children = [
        TreeNode("除斑雷射"),
        TreeNode("除毛雷射"),
        TreeNode("緊膚雷射")
    ]
    
    # Level 3 - 注射治療的子項目
    injection.children = [
        TreeNode("玻尿酸"),
        TreeNode("肉毒桿菌")
    ]
    
    return root

def create_tree2():
    # Tree 2: 以治療部位為主的分類
    root = TreeNode("醫學美容")
    
    # Level 1
    face = TreeNode("臉部治療")
    body = TreeNode("身體治療")
    root.children = [face, body]
    
    # Level 2 - 臉部治療的子項目
    face.children = [
        TreeNode("注射治療"),  # 共同節點
        TreeNode("臉部拉提"),
        TreeNode("除斑雷射")   # 共同節點
    ]
    
    # Level 2 - 身體治療的子項目
    body.children = [
        TreeNode("體雕"),
        TreeNode("除毛雷射")   # 共同節點
    ]
    
    return root

# 輔助函數：更好地視覺化樹結構
def print_tree_visual(root, common_nodes=None, prefix="", is_last=True):
    if not root:
        return
        
    # 決定當前層級的連接線樣式
    connector = "└── " if is_last else "├── "
    # 決定子節點的縮排樣式
    child_prefix = prefix + ("    " if is_last else "│   ")
    
    # 添加共同節點標記
    node_text = root.val
    if common_nodes and root.val in common_nodes:
        node_text += " [*]"  # 使用 [*] 標記共同節點
    
    # 印出當前節點
    print(prefix + connector + node_text)
    
    # 遞迴處理所有子節點
    for i, child in enumerate(root.children):
        is_last_child = (i == len(root.children) - 1)
        print_tree_visual(child, common_nodes, child_prefix, is_last_child)

# 建立並印出兩棵樹
tree1 = create_tree1()
tree2 = create_tree2()

print("\n第一棵樹 (治療方式分類):")
print_tree_visual(tree1)
print("\n第二棵樹 (治療部位分類):")
print_tree_visual(tree2)

# 使用先前定義的合併算法
def merge_trees(root1, root2):
    # 用於存儲共同節點的集合
    common_nodes = set()
    
    def create_node_map(root, node_map):
        if not root:
            return
        node_map[root.val] = root
        for child in root.children:
            create_node_map(child, node_map)
    
    def find_common_nodes(map1, map2):
        return set(map1.keys()) & set(map2.keys())
    
    def merge_from_node(node1, node2, merged_nodes):
        if not node1 or not node2:
            return node1 or node2
            
        if node1.val in merged_nodes:
            return node1
            
        merged_nodes.add(node1.val)
        merged_node = TreeNode(node1.val)
        
        # 如果節點在兩棵樹中都存在，標記為共同節點
        if node1.val == node2.val:
            common_nodes.add(node1.val)
        
        children_values = set()
        children_nodes = []
        
        for child1 in node1.children:
            if child1.val not in children_values:
                children_values.add(child1.val)
                matching_child2 = next((c for c in node2.children if c.val == child1.val), None)
                children_nodes.append(merge_from_node(child1, matching_child2, merged_nodes))
        
        for child2 in node2.children:
            if child2.val not in children_values:
                children_values.add(child2.val)
                children_nodes.append(merge_from_node(child2, child2, merged_nodes))
        
        merged_node.children = children_nodes
        return merged_node
    
    if not root1 or not root2:
        return root1 or root2, common_nodes
        
    if root1.val != root2.val:
        return None, common_nodes
        
    merged_nodes = set()
    return merge_from_node(root1, root2, merged_nodes), common_nodes

# 合併兩棵樹並印出結果
merged_tree, common_nodes = merge_trees(tree1, tree2)
print("\n合併後的樹 (標記 [*] 為共同節點):")
print_tree_visual(merged_tree, common_nodes)

def save_tree_to_file(root, filename):
    """將樹結構保存到文件中"""
    def write_node(node, level, file):
        indent = "    " * level
        file.write(f"{indent}{node.val}\n")
        for child in node.children:
            write_node(child, level + 1, file)
            
    with open(filename, 'w', encoding='utf-8') as f:
        write_node(root, 0, f)

def load_tree_from_file(filename):
    """從文件中讀取樹結構"""
    def count_indent(line):
        return len(line) - len(line.lstrip())
    
    def create_node_from_line(line):
        return TreeNode(line.strip())
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = [line.rstrip() for line in f.readlines() if line.strip()]
    
    if not lines:
        return None
    
    root = create_node_from_line(lines[0])
    stack = [(root, 0)]
    
    for line in lines[1:]:
        indent = count_indent(line)
        level = indent // 4  # 每個縮排級別為4個空格
        node = create_node_from_line(line)
        
        # 找到正確的父節點
        while stack and stack[-1][1] >= level:
            stack.pop()
        
        if stack:
            parent = stack[-1][0]
            parent.children.append(node)
        
        stack.append((node, level))
    
    return root

# 新增主程式部分
if __name__ == "__main__":
    import sys
    
    # 保存現有的兩棵樹到文件
    tree1 = create_tree1()
    tree2 = create_tree2()
    
    save_tree_to_file(tree1, "tree1.txt")
    save_tree_to_file(tree2, "tree2.txt")
    
    # 讀取第三棵樹（如果存在）
    try:
        tree3 = load_tree_from_file("tree3.txt")
        print("\n第三棵樹 (從文件讀取):")
        print_tree_visual(tree3)
        
        # 先合併前兩棵樹
        intermediate_tree, common_nodes_1_2 = merge_trees(tree1, tree2)
        print("\n前兩棵樹合併結果 (標記 [*] 為共同節點):")
        print_tree_visual(intermediate_tree, common_nodes_1_2)
        
        # 再與第三棵樹合併
        final_tree, final_common_nodes = merge_trees(intermediate_tree, tree3)
        print("\n最終合併結果 (標記 [*] 為共同節點):")
        print_tree_visual(final_tree, final_common_nodes)
        
        # 保存最終結果
        save_tree_to_file(final_tree, "merged_result.txt")
        
    except FileNotFoundError:
        print("\n未找到 tree3.txt，只合併兩棵樹:")
        merged_tree, common_nodes = merge_trees(tree1, tree2)
        print_tree_visual(merged_tree, common_nodes)
        save_tree_to_file(merged_tree, "merged_result.txt")

# 讀取獲利模式樹和市場價值樹
benefit_tree1 = load_tree_from_file("benefit1.txt")
benefit_tree2 = load_tree_from_file("benefit2.txt")

print("\n獲利模式分類樹:")
print_tree_visual(benefit_tree1)

print("\n市場價值分類樹:")
print_tree_visual(benefit_tree2)

# 合併兩棵樹
merged_benefit_tree, common_benefit_nodes = merge_trees(benefit_tree1, benefit_tree2)

print("\n合併後的商業評價樹 (標記 [*] 為共同節點):")
print_tree_visual(merged_benefit_tree, common_benefit_nodes)

# 保存合併結果
save_tree_to_file(merged_benefit_tree, "merged_benefit_result.txt")