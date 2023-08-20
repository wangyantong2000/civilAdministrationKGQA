import torch
import torch.nn as nn
from torch.nn import functional as F
from transformers import BertModel, BertPreTrainedModel, BertConfig, AdamW, BertTokenizer
from torch.nn.modules import BCEWithLogitsLoss
device = 'cuda' if torch.cuda.is_available() else 'cpu'
alpha, beta, gamma = 1, 1, 1
class BertQueryNER(BertPreTrainedModel):
    def __init__(self, config):
        super(BertQueryNER, self).__init__(config)

        self.bert = BertModel(config)  # Bert
        self.start_outputs = nn.Linear(config.hidden_size, 1)  # 开始位置分类器 Start Output Classifier
        self.end_outputs = nn.Linear(config.hidden_size, 1)  # 结束位置分类器 End Output Classifier
        self.span_embedding = MultiNonLinearClassifier(config.hidden_size * 2, 1,
                                                       # 边界匹配分类器 Span Match Output Classifier
                                                       config.mrc_dropout,
                                                       intermediate_hidden_size=config.classifier_intermediate_hidden_size)

        self.hidden_size = config.hidden_size

        self.init_weights()  # 权重初始化

    def forward(self, input_ids, token_type_ids=None, attention_mask=None):
        """
        Args:
            input_ids: bert input tokens, tensor of shape [seq_len]
            token_type_ids: 0 for query, 1 for context, tensor of shape [seq_len]
            attention_mask: attention mask, tensor of shape [seq_len]
        Returns:
            start_logits: start/non-start probs of shape [seq_len]
            end_logits: end/non-end probs of shape [seq_len]
            match_logits: start-end-match probs of shape [seq_len, 1]
        """

        # Step 1: 获得所有token的BERT词嵌入
        bert_outputs = self.bert(input_ids, token_type_ids=token_type_ids, attention_mask=attention_mask)
        sequence_heatmap = bert_outputs[0]  # [batch, seq_len, hidden]
        batch_size, seq_len, hid_size = sequence_heatmap.size()

        # Step 2: 计算 tokens 是开始位置的 logits 预测值
        start_logits = self.start_outputs(sequence_heatmap).squeeze(-1)  # [batch, seq_len, 1]#降维

        # Step 3: 计算 tokens 是结束位置的 logits 预测值
        end_logits = self.end_outputs(sequence_heatmap).squeeze(-1)  # [batch, seq_len, 1]#增维

        # Step 4: 逐个拼接句子中所有的 tokens 为 Span Match Output Classifier 做准备，
        #         最后做成一个shape为[batch, seq_len, seq_len, hidden*2]的张量span_matrix。
        start_extend = sequence_heatmap.unsqueeze(2).expand(-1, -1, seq_len, -1)  # [batch, seq_len, seq_len, hidden]
        end_extend = sequence_heatmap.unsqueeze(1).expand(-1, seq_len, -1, -1)  # [batch, seq_len, seq_len, hidden]

        span_matrix = torch.cat([start_extend, end_extend], 3)  # [batch, seq_len, seq_len, hidden*2]#按第三维拼接

        # Step 5: 计算 span matrix 中的 logits 预测值，
        #         从 span matrix 中的 [batch, seq_len, seq_len, hidden*2] 变成 span_logits 中的[batch, seq_len, seq_len]
        #         其中 span_logits[i][j] 表示第 i 个 tokens 作为开始位置，第 j 个 tokens 作为结束位置的匹配预测值。
        span_logits = self.span_embedding(span_matrix).squeeze(-1)  # [batch, seq_len, seq_len]


        return start_logits, end_logits, span_logits


class MultiNonLinearClassifier(nn.Module):
    def __init__(self, hidden_size, num_label, dropout_rate, act_func="gelu", intermediate_hidden_size=None):
        super(MultiNonLinearClassifier, self).__init__()

        self.num_label = num_label
        self.intermediate_hidden_size = hidden_size if intermediate_hidden_size is None else intermediate_hidden_size
        self.classifier1 = nn.Linear(hidden_size, self.intermediate_hidden_size)
        self.classifier2 = nn.Linear(self.intermediate_hidden_size, self.num_label)
        self.dropout = nn.Dropout(dropout_rate)
        self.act_func = act_func

    def forward(self, input_features):
        """
        令 input_features 为 X，output_features 为 O，则forward的逻辑就是一个MLP：
        O = W2 \cdot dropout(activete(W1 \cdot X))
        """

        features_output1 = self.classifier1(input_features)

        if self.act_func == "gelu":
            features_output1 = F.gelu(features_output1)
        elif self.act_func == "relu":
            features_output1 = F.relu(features_output1)
        elif self.act_func == "tanh":
            features_output1 = F.tanh(features_output1)
        else:
            raise ValueError
        features_output1 = self.dropout(features_output1)
        features_output2 = self.classifier2(features_output1)
        return features_output2


class BertQueryNerConfig(BertConfig):
    def __init__(self, **kwargs):
        super(BertQueryNerConfig, self).__init__(**kwargs)
        self.mrc_dropout = kwargs.get("mrc_dropout", 0.1)
        self.classifier_intermediate_hidden_size = kwargs.get("classifier_intermediate_hidden_size", 1024)
        self.classifier_act_func = kwargs.get("classifier_act_func", "gelu")


def compute_loss(start_logits, end_logits, span_logits,
                 start_labels, end_labels, match_labels,
                 start_label_mask, end_label_mask):


    batch_size, seq_len = start_logits.size()
    bce_loss = BCEWithLogitsLoss(reduction='none')

    start_float_label_mask = start_label_mask.view(-1).float()  # shape=batch x n
    end_float_label_mask = end_label_mask.view(-1).float()
    match_label_row_mask = start_label_mask.bool().unsqueeze(-1).expand(-1, -1, seq_len)
    match_label_col_mask = end_label_mask.bool().unsqueeze(-2).expand(-1, seq_len, -1)
    match_label_mask = match_label_row_mask & match_label_col_mask
    match_label_mask = torch.triu(match_label_mask, 0)  # start should be less equal to end

    float_match_label_mask = match_label_mask.view(batch_size, -1).float()

    start_loss = bce_loss(start_logits.view(-1), start_labels.view(-1).float())
    start_loss = (start_loss * start_float_label_mask).sum() / start_float_label_mask.sum()
    end_loss = bce_loss(end_logits.view(-1), end_labels.view(-1).float())
    end_loss = (end_loss * end_float_label_mask).sum() / end_float_label_mask.sum()
    match_loss = bce_loss(span_logits.view(batch_size, -1), match_labels.view(batch_size, -1).float())
    match_loss = match_loss * float_match_label_mask
    match_loss = match_loss.sum() / (float_match_label_mask.sum() + 1e-10)

    return start_loss, end_loss, match_loss


def query_span_f1(start_preds, end_preds, match_logits, start_label_mask, end_label_mask, match_labels, flat=False):
    """
    根据模型的输出，计算span的F1值。
    Args:
        start_preds: [bsz, seq_len]
        end_preds: [bsz, seq_len]
        match_logits: [bsz, seq_len, seq_len]
        start_label_mask: [bsz, seq_len]
        end_label_mask: [bsz, seq_len]
        match_labels: [bsz, seq_len, seq_len]
        flat: if True, decode as flat-ner
    Returns:
        span-f1 counts, tensor of shape [3]: tp, fp, fn
    """
    # 将0或1值转换成布尔值
    start_label_mask = start_label_mask.bool()
    end_label_mask = end_label_mask.bool()
    match_labels = match_labels.bool()

    bsz, seq_len = start_label_mask.size()

    match_preds = match_logits > 0  # [bsz, seq_len, seq_len]
    start_preds = start_preds.bool()  # [bsz, seq_len]
    end_preds = end_preds.bool()  # [bsz, seq_len]

    match_preds = (match_preds & start_preds.unsqueeze(-1).expand(-1, -1, seq_len) & end_preds.unsqueeze(1).expand(-1,
                                                                                                                   seq_len,
                                                                                                                   -1))  # 让start、end（expand之后）和match对应位置进行与运算
    match_label_mask = (
                start_label_mask.unsqueeze(-1).expand(-1, -1, seq_len) & end_label_mask.unsqueeze(1).expand(-1, seq_len,
                                                                                                            -1))  # 根据start和end的mask算出match的mask
    match_label_mask = torch.triu(match_label_mask, 0)  # 保证实体开始的位置小于等于结束的位置
    match_preds = match_label_mask & match_preds

    tp = (match_labels & match_preds).long().sum()  # TRUE POSITIVE TP、True Positive 真阳性：预测为正，实际也为正
    fp = (~match_labels & match_preds).long().sum()  # FALSE POSITIVE FP、False Positive 假阳性：预测为正，实际为负
    fn = (match_labels & ~match_preds).long().sum()  # FALSE NEGETIVE FN、False Negative 假阴性：预测与负、实际为正
    return torch.stack([tp, fp, fn])


