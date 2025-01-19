from ner.ner_processor import NERProcessor
from ner.entity_filter import EntityFilter
from knowledge_bases.concept_tree_manager import ConceptTreeManager

def main():
    # 範例文本
    text = """王正坤醫師，藝群醫學美容集團董事長、藝群皮膚科診所院長、Dr.FreeVenus藝群保養品創辦人(玻尿酸精華液領導品牌)、藝群國際企業董事長，學歷：台北醫學大學醫學系、成功大學管理學碩士、長榮大學企管博士，經歷：中華民國行政院政務顧問、台灣醫用雷射光電學會理事長、台灣美容醫療促進協會理事長、台南市醫師公會理事長、成功大學EMBA校友總會理事長、大台南觀光聯盟理事長、亞洲皮膚科醫學會院士(AADV)、成功大學EMBA企管碩士班老師(授課連鎖企業經營管理)、成功大學附設醫院皮膚科兼任主治醫師(授課美容醫學)、長榮大學經營管理博士班老師(授課品牌管理、供應鏈管理)、中華醫事科技大學講座教授(醫學美容、醫務管理)、長榮大學校友會全國總會理事長、中華民國醫師公會全國聯合會常務理事、中華民國醫師公會全國聯合會常務監事、台灣皮膚科醫學會常務理事、國際醫療衛生促進協會監事長、衛生福利部美容醫學教育訓練委員、衛生福利部醫療器材評估專家、醫策會病人安全委員、台南市政府市政顧問、台南市安南醫院BOT委員、台南市政府公害糾紛調處委員會委員、台南市政府醫事審議委員會委員、台南市政府教育審議委員會委員、台南地方法院醫療專業調解委員、台南地方法院醫事類專家諮詢委員，得獎：台灣醫療典範獎、台灣醫療服務傑出獎、國家品牌玉山獎傑出企業領導人、台灣100大MVP經理人、衛生福利部AED「救命天使」獎、終身成就獎-台南市醫師公會、勞動部績優企業獎、台南地區傑出總經理CEO、美國BGS(Beta Gamma Sigma)國際商學會榮譽會員、台北醫學大學傑出校友、長榮大學傑出校友、中華民國斐陶斐榮譽學會榮譽會員。"""  # 您的完整文本
    
    # 1. NER 處理
    ner_processor = NERProcessor()
    entities = ner_processor.process_text(text)
    ner_processor.save_results(entities, 'ner_results.json')
    
    # 2. 實體過濾和分類
    entity_filter = EntityFilter()
    categorized_entities = entity_filter.filter_medical_entities(entities)
    
    # 3. 生成概念樹
    tree_manager = ConceptTreeManager()
    concept_trees = tree_manager.generate_trees(categorized_entities)
    tree_manager.save_trees(concept_trees, 'concept_trees.json')
    
    # 4. 輸出結果
    print("\n分類後的實體:")
    for category, entities in categorized_entities.items():
        if entities:
            print(f"\n{category}:")
            for entity in entities:
                print(f"- {entity}")
    
    print("\n生成的概念樹已儲存到 data/trees/concept_trees.json")

if __name__ == "__main__":
    main()