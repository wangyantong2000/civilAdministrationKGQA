import torch
from transformers import BertTokenizer
import numpy as np

device = 'cuda' if torch.cuda.is_available() else 'cpu'
alpha, beta, gamma = 1, 1, 1


def extract_nested_spans(start_preds, end_preds, match_preds, start_label_mask, end_label_mask):
    start_label_mask = start_label_mask.bool()
    end_label_mask = end_label_mask.bool()
    bsz, seq_len = start_label_mask.size()
    start_preds = start_preds.bool()
    end_preds = end_preds.bool()

    match_preds = (match_preds & start_preds.unsqueeze(-1).expand(-1, -1, seq_len) & end_preds.unsqueeze(1).expand(-1,
                                                                                                                   seq_len,
                                                                                                                   -1))
    match_label_mask = (
                start_label_mask.unsqueeze(-1).expand(-1, -1, seq_len) & end_label_mask.unsqueeze(1).expand(-1, seq_len,
                                                                                                            -1))
    match_label_mask = torch.triu(match_label_mask, 0)  # start should be less or equal to end
    match_preds = match_label_mask & match_preds
    match_pos_pairs = np.transpose(np.nonzero(match_preds.numpy())).tolist()
    return [(pos[1], pos[2]) for pos in match_pos_pairs]


def pre(context, trained_model):
    entity = ['业务', '身份', '条件', '组织部门', '证件', '物品', '期间', '规则', '义务', '权利']
    query = ['找出业务：指某种有目的的工作或工作项目具体。例子：婚姻登记',
             '找出身份：指人的出身和社会地位。例子：要求结婚的男女双方、婚姻登记员',
             '找出条件：指制约事物发生、存在或发展的因素。例子：重婚的、有禁止结婚的亲属关系的',
             '找出组织部门：指中央及地方的全部行政、官僚机关。例子：婚姻登记机关',
             '找出证件：指用来证明的证书和文件。例子：本人的户口簿、身份证',
             #'找出物品：是生产、办公、生活领域常用的一个概念，这里指业务中处理的物质资料。例子：同居期间所得的财产',
             '找出期间：指时间范围。例子：婚姻关系存续期间',
             '找出规则：指办事的依据、法规。例子：便民原则、中华人民共和国婚姻法',
             '找出义务：情愿、志愿、应该做的事。例子：实行计划生育',
             '找出权利：指赋予人实现其利益的一种力量。例子：各用自己姓名']
    tokenizer_path = r'pretrained_model'
    tokenizer = BertTokenizer.from_pretrained(tokenizer_path)
    max_length = 512
    dict = {}
    for i in query:
        input_ids_1 = [tokenizer.convert_tokens_to_ids(c) for c in i]  # inputs_ids_1表示输入模板的token id
        input_ids_1 = [tokenizer.cls_token_id] + input_ids_1 + [tokenizer.sep_token_id]
        token_type_ids_1 = [0] * len(input_ids_1)
        start_ids_1 = end_ids_1 = [0] * len(input_ids_1)
        input_ids_2 = [tokenizer.convert_tokens_to_ids(c) for c in context]  # inputs_ids_2表示数据集中每句话的token id
        input_ids_2 = input_ids_2 + [tokenizer.sep_token_id]
        input_ids = input_ids_1 + input_ids_2
        token_type_ids_2 = [1] * len(input_ids_2)
        token_type_ids = token_type_ids_1 + token_type_ids_2
        label_mask1 = [0] * len(token_type_ids_1)
        label_mask2 = [1] * len(token_type_ids_2)
        label_mask2[-1] = 0
        label_mask = label_mask1 + label_mask2
        start_label_mask = label_mask.copy()
        end_label_mask = label_mask.copy()
        tokens = input_ids[: max_length]
        type_ids = token_type_ids[: max_length]
        start_label_mask = start_label_mask[: max_length]
        end_label_mask = end_label_mask[: max_length]
        sep_token = tokenizer.sep_token_id
        if tokens[-1] != sep_token:
            assert len(tokens) == max_length
            tokens = tokens[: -1] + [sep_token]
            start_label_mask[-1] = 0
            end_label_mask[-1] = 0
        tokens = torch.LongTensor([tokens])
        token_type_ids = torch.LongTensor([type_ids])
        start_label_mask = torch.LongTensor([start_label_mask])
        end_label_mask = torch.LongTensor([end_label_mask])
        attention_mask = (tokens != 0).long()
        with torch.no_grad():
            start_logits, end_logits, span_logits = trained_model(tokens, attention_mask=attention_mask,
                                                                  token_type_ids=token_type_ids)
        # print(start_logits, end_logits, span_logits)
        start_preds, end_preds, span_preds = start_logits > 0, end_logits > 0, span_logits > 0
        match_preds = span_logits > 0
        tokens1 = tokens.tolist()
        x = tokenizer.convert_ids_to_tokens(tokens1[0])
        x = [z if z != '[UNK]' else ' ' for z in x]
        sentence = ''.join(x).split('[SEP]')
        q = sentence[0][5:].split('：')
        l = len(i) + 2
        infer_pos = extract_nested_spans(start_preds, end_preds, match_preds, start_label_mask, end_label_mask)

        s = -1
        e = -1
        if infer_pos != []:
            dict[q[0][2:]] = []
            for infer_po in infer_pos:
                if dict[q[0][2:]] != [] and ((infer_po[0] == s) or (infer_po[1] == e)):
                    if e - s < infer_po[1] - infer_po[0]:
                        dict[q[0][2:]].pop()
                    else:
                        continue
                s = infer_po[0]
                e = infer_po[1]
                n = x[infer_po[0]:infer_po[1] + 1]

                print(n)

                n = ''.join(n) + f',{infer_po[0] - l},{infer_po[1] - l}'
                dict[q[0][2:]].append(n)
    return dict


def ner_pre(context):
    trained_model = torch.load(r'ner_modelxxxx.pth', map_location=torch.device('cpu'))
    trained_model.eval()
    ner = pre(context, trained_model)
    print(ner)
    yw = []  # 业务
    sf = []  # 身份
    zzbm = []  # 组织部门
    zj = []  # 证件
    wp = []  # 物品
    yiw = []  # 义务
    if '业务' in ner.keys():
        for n in ner['业务']:
            n = n.split(',')
            yw.append(n[0])
    if '身份' in ner.keys():
        for n in ner['身份']:
            n = n.split(',')
            sf.append(n[0])
    if '组织部门' in ner.keys():
        for n in ner['组织部门']:
            n = n.split(',')
            zzbm.append(n[0])
    if '证件' in ner.keys():
        for n in ner['证件']:
            n = n.split(',')
            zj.append(n[0])
    if '物品' in ner.keys():
        for n in ner['物品']:
            n = n.split(',')
            wp.append(n[0])
    if '义务' in ner.keys():
        for n in ner['义务']:
            n = n.split(',')
            yiw.append(n[0])

    return yw, sf, zzbm, zj, wp, yiw


if __name__ == '__main__':
    data = '抚养的义务'
    yw, sf, zzbm, zj, wp, yiw = ner_pre(data)
    R = set(yw + sf + zzbm + zj + wp + yiw)
    print(R)
