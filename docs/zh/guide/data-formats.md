# 数据格式

本页汇总平台消费和产出的所有文件格式。

## SMILES 字符串

平台使用 **RDKit** 解析 SMILES。实际含义：

- 接受标准 Daylight SMILES 表示法。
- 支持芳香简写（如 `c1ccccc1`）。
- 立体化学标记（`/`、`\`、`@`、`@@`）可接受但模型不使用。
- 使用 `.` 分隔符的多组分 SMILES（如 `[Na+].[Cl-]`）可解析，但模型将整个字符串作为单一分子图特征化。对于盐类，通常更适合将各组分分别分配到 **API** 和 **Coformer** 字段。

::: tip
若 SMILES 解析失败，从 [PubChem](https://pubchem.ncbi.nlm.nih.gov/) 获取目标化合物的 *Canonical SMILES*。RDKit 几乎不会拒绝这类输入。
:::

## 批量筛选 CSV（输入）

用于 [批量筛选](./batch)。

```csv
api_smiles,coformer_smiles
CCO,O=C(O)c1ccccc1O
O=C(O)CCC(=O)O,Nc1ccnc(N)[n+]1[O-]
```

| 规则 | 详情 |
| --- | --- |
| **列** | 恰好两列：`api_smiles`、`coformer_smiles` |
| **表头行** | 可选。若第一行包含 `smiles` 字样（不区分大小写），将被视为表头并跳过 |
| **编码** | UTF-8 |
| **无效行** | 空行或字段数不正确的行被静默丢弃 |

在批量筛选页面点击 **下载模板** 获取模板文件。

## 微调 CSV（输入）

用于 [模型微调](./finetune)。

```csv
api_smiles,coformer_smiles,label
CCO,O=C(O)c1ccccc1O,2
c1ccccc1,CC(=O)O,0
```

| 规则 | 详情 |
| --- | --- |
| **列** | 恰好三列：`api_smiles`、`coformer_smiles`、`label` |
| **标签值** | `{0, 1, 2, 3}` 中的整数——参见下方类别映射 |
| **表头行** | **必需**（解析器使用 Python `csv.DictReader`） |
| **最少行数** | 2 行有效数据（两侧 SMILES 均可解析，标签有效） |
| **无效行** | 被静默丢弃 |

类别映射：

| 标签 | 类别 |
| :---: | --- |
| `0` | Negative |
| `1` | Salt |
| `2` | Cocrystal |
| `3` | Solvate |

在微调页面点击 **下载模板** 获取模板文件。

## 批量结果 CSV（导出）

在批量筛选结果卡片点击 **导出 CSV** 后获得。

```csv
API SMILES,Coformer SMILES,Prediction,Label,Confidence
"CCO","O=C(O)c1ccccc1O",2,Cocrystal,89.1%
"O=C(O)CCC(=O)O","Nc1ccnc(N)[n+]1[O-]",1,Salt,76.4%
```

| 列 | 说明 |
| --- | --- |
| `API SMILES`、`Coformer SMILES` | 带引号；从输入回显 |
| `Prediction` | 整数类别标签（`0`–`3`） |
| `Label` | 人类可读类别名称 |
| `Confidence` | 最大类别概率，以百分比表示 |

::: info
导出仅包含预测类别及其置信度。完整的四分类概率向量可通过平台 REST API 获取。
:::

## REST API

如需程序化访问，平台提供基于 Token 认证的 REST API。完整端点参考记录在 [项目 README](https://github.com/PolarSnowLeopard/MCC-GCN-App#-api-reference) 中。
