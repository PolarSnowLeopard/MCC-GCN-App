# 数据格式

平台所消费或产出的所有 CSV / SMILES 格式都集中在这一页。

## SMILES

平台用 **RDKit** 解析 SMILES。实际上意味着：

- 标准 Daylight SMILES 接受。
- 芳香记号（`c1ccccc1`）可用。
- 立体化学记号（`/`、`\`、`@`）接受但模型不使用。
- 多组分 SMILES（如 `[Na+].[Cl-]`，用 `.` 隔开）能解析，但会被特征化为一个分子——大多数情况下你应该把盐拆到 API / Coformer 两个槽里输入。

::: tip 解析失败时
从 PubChem 复制该分子的 *Canonical SMILES* 粘贴。RDKit 几乎不会拒绝它们。
:::

## 批量筛选 CSV

[批量筛选 → 上传 CSV](./batch#上传-csv) 使用。

```csv
api_smiles,coformer_smiles
CCO,O=C(O)c1ccccc1O
O=C(O)CCC(=O)O,Nc1ccnc(N)[n+]1[O-]
```

规则：

- **两列**：`api_smiles`、`coformer_smiles`。
- **表头行**：可选。第一行如果包含单词 `smiles`（不区分大小写）会被跳过。
- **编码**：UTF-8。
- **空行 / 不完整行**：静默丢弃。

批量页 **下载模板** 按钮可以下到一个可用模板。

## 微调 CSV

[模型微调 → 训练数据](./finetune#第-1-步准备训练数据) 使用。

```csv
api_smiles,coformer_smiles,label
CCO,O=C(O)c1ccccc1O,2
c1ccccc1,CC(=O)O,0
```

规则：

- **三列**：`api_smiles`、`coformer_smiles`、`label`。
- **label** 必须是 `0..3` 的整数，对应平台类别：

| 标签 | 类别 |
| --- | --- |
| `0` | `Negative` |
| `1` | `Salt` |
| `2` | `Cocrystal` |
| `3` | `Solvate` |

- **最少**：2 行有效数据。（解析失败的行会被静默丢弃。）
- **表头行**：必须（解析器使用 `DictReader`）。

微调页 **下载模板** 按钮可以下到起始 CSV。

## 批量结果导出 CSV

在批量结果卡片点 **导出 CSV** 后下载到的内容：

```csv
API SMILES,Coformer SMILES,Prediction,Label,Confidence
"CCO","O=C(O)c1ccccc1O",2,Cocrystal,89.1%
"O=C(O)CCC(=O)O","Nc1ccnc(N)[n+]1[O-]",1,Salt,76.4%
```

字段：

| 列 | 说明 |
| --- | --- |
| `API SMILES`、`Coformer SMILES` | 加引号；从输入回显 |
| `Prediction` | 整数类别标签（0–3） |
| `Label` | 人类可读标签（`Negative` / `Salt` / `Cocrystal` / `Solvate`） |
| `Confidence` | 最大概率（百分比） |

注意：导出有意省略了完整概率向量（只保留预测类别 + 其置信度）。如果你需要完整向量，请使用平台的 REST API。

## REST API

如果需要自动化集成，平台还提供 Token 鉴权的 REST API。完整参考见 [项目 README](https://github.com/PolarSnowLeopard/MCC-GCN-App#-api-reference)。
