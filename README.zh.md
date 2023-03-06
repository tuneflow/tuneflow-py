# TuneFlow Python SDK

[English](./README.md) | [简体中文](./README.zh.md)

![TuneFlow Screenshots](docs/images/tuneflow_wall_thin.jpg)

[![Build Status](https://dev.azure.com/zeostudio/tuneflow-public/_apis/build/status/tuneflow.tuneflow-py?branchName=main)](https://dev.azure.com/zeostudio/tuneflow-public/_build/latest?definitionId=32&branchName=main)
[![Code Coverage](https://img.shields.io/azure-devops/coverage/zeostudio/tuneflow-public/32/main?logo=azure-pipelines)](https://dev.azure.com/zeostudio/tuneflow-public/_build/latest?definitionId=32&branchName=main)
[![PyPI](https://img.shields.io/pypi/v/tuneflow-py?color=blue&label=tuneflow-py&logo=pypi)](https://pypi.org/project/tuneflow-py/)
[![Discord](https://img.shields.io/discord/1076012137161424906?color=%237289da&logo=discord)](https://discord.com/channels/1076012137161424906/1076012755250851860)
![License](https://img.shields.io/github/license/tuneflow/tuneflow-py)

## 什么是 `TuneFlow` 和 `tuneflow-py`?

[TuneFlow](https://www.tuneflow.com) 是 AI 驱动的新一代 DAW (数字音乐工作站)。与传统 DAW 不同的是，与它深度集成的插件系统可以支持端到端的完整音乐制作流程，比如**作曲**, **编曲**, **自动化**, **混音**, **转录** 等等...... 你可以轻松地将你的音乐算法或 AI 模型集成到 TuneFlow 中，所有的更改会即时反映到 DAW 中，与你的日常制作流程融为一体。

`tuneflow-py` 是用于开发 Python 版本 TuneFlow 插件的 依赖库.

## 安装

```bash
pip install tuneflow-py
```

## 使用别的编程语言?

以下是为其他编程语言开发的 SDK:

- **Typescript**: https://www.github.com/tuneflow/tuneflow
- 其他: 欢迎贡献第三方 SDK!

## 为什么开发 TuneFlow 插件?

TuneFlow 插件系统的核心宗旨是让开发者只需要关注数据模型，而无需关注底层的各种实现。换句话说，一个 TuneFlow 插件的唯一使命就是按照自己的需求去修改当前曲目的数据模型。插件运行完成后，TuneFlow 会自动检测被更改的部分，并对当前工程做出相应的调整。

与传统的 DAW 插件只能处理来自一条轨道的 MIDI/音频信号不同，这个插件系统允许你访问和修改项目中的任何部分，这使得 TuneFlow 的插件系统能够轻松集成系统性的音乐算法和 AI 模型。

不仅如此，TuneFlow 的插件系统还支持远程处理。这意味着你可以在本地编写和测试插件，然后在任何地方部署它，DAW 可以通过简单的网络请求来运行你的插件。

以下是插件系统的运行流程示意图:

![插件运行流程](docs/images/pipeline_flow_en.jpg)

## 开始开发插件

请参阅 TuneFlow 开发者文档： [https://help.tuneflow.com/zh/developer](https://help.tuneflow.com/zh/developer)

## 插件展示

### ⌨️ AudioLDM

根据文本提示生成语音、音效、音乐等等。

代码库: https://github.com/tuneflow/AudioLDM

<img src="./docs/images/demos/audioldm_cn.gif" width="500" />

### 🎙️ 歌声转录 MIDI

将一段可能带背景噪音或背景音乐的人声音频转录为 MIDI。

代码库: https://github.com/tuneflow/singing-transcription-plugin

<img src="./docs/images/demos/singing_transcription_icassp2021.gif" width="500" />

### 🥁 Pocket Drum

根据给定的风格以及旋律生成一段鼓点。

代码库: 即将更新.

<img src="./docs/images/demos/pocket_drum_cn.gif" width="500" />

欢迎访问 https://www.github.com/tuneflow/tuneflow-py-demos 了解更多示例插件。

## 贡献代码

请参阅 [贡献指南](./CONTRIBUTE.md).

## 其他资源

[TuneFlow 官网](https://tuneflow.com)

[Typescript SDK](https://www.github.com/tuneflow/tuneflow)
