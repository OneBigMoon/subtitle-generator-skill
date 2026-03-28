#!/usr/bin/env python3
"""
字幕生成器 - 基于口播稿和音频生成 SRT 字幕文件

核心功能：
1. 使用 Whisper 从音频提取词级时间戳
2. 将词级时间戳转换为字符级时间戳
3. 对口播稿进行智能分段（10-15字为一段，标点为分隔）
4. 将分段后的口播稿与字符级时间戳对齐
5. 生成最终的 SRT 字幕文件

特点：
- 完全本地运行，无需外部 API Key
- 支持多种 Whisper 模型（tiny, base, small, medium, large）
- 智能处理中文口播稿的分段和对齐
"""

import re
import os
import argparse
from typing import List, Dict, Tuple, Optional
from difflib import SequenceMatcher


class ScriptSegmenter:
    """口播稿分段器 - 将长文本智能分段成适合字幕的短句"""

    def __init__(self, min_chars: int = 10, max_chars: int = 15, min_segment_length: int = 5):
        """
        初始化分段器

        Args:
            min_chars: 每段最少字数（默认10）
            max_chars: 每段最多字数（默认15）
            min_segment_length: 遇到主要标点时的最小段长度（默认5）
        """
        self.min_chars = min_chars
        self.max_chars = max_chars
        self.min_segment_length = min_segment_length

        # 定义主要标点（句子结束）和次要标点（句子中间）
        self.main_punct = '。！？'  # 主要标点：句子结束
        self.secondary_punct = '，、；：'  # 次要标点：句子中间
        self.all_punct = self.main_punct + self.secondary_punct

    def segment(self, script_text: str) -> List[Dict]:
        """
        将口播稿分段

        Args:
            script_text: 口播稿文本

        Returns:
            分段列表，每段包含：
            - text: 段落文字
            - length: 段落字数
            - index: 段落序号（从1开始）
        """
        # 清理文本
        script_clean = script_text.replace(' ', '').replace('\n', '')

        segments = []
        current_segment = ""

        i = 0
        while i < len(script_clean):
            char = script_clean[i]

            # 正常处理所有字符（包括括号）
            current_segment += char

            # 如果遇到标点
            if char in self.all_punct:
                # 检查是否需要分段
                should_split = False

                # 情况1：遇到主要标点，且当前段长度>=最小段长度
                if char in self.main_punct and len(current_segment) >= self.min_segment_length:
                    should_split = True

                # 情况2：遇到次要标点，且当前段长度>=最小字数
                elif char in self.secondary_punct and len(current_segment) >= self.min_chars:
                    should_split = True

                # 情况3：当前段长度达到最大字数，必须分段
                elif len(current_segment) >= self.max_chars:
                    should_split = True

                if should_split and current_segment:
                    segments.append({
                        'text': current_segment,
                        'length': len(current_segment)
                    })
                    current_segment = ""

            # 检查是否超长（超过最大字数）
            if len(current_segment) >= self.max_chars:
                # 寻找当前段中最后一个标点的位置
                last_punct_pos = -1
                for j in range(len(current_segment) - 1, -1, -1):
                    if current_segment[j] in self.all_punct:
                        last_punct_pos = j
                        break

                # 如果找到标点且不在开头，在此处分割
                if last_punct_pos > 0:
                    split_text = current_segment[:last_punct_pos + 1]
                    remaining = current_segment[last_punct_pos + 1:]

                    segments.append({
                        'text': split_text,
                        'length': len(split_text)
                    })
                    current_segment = remaining

            i += 1

        # 处理最后一段
        if current_segment:
            segments.append({
                'text': current_segment,
                'length': len(current_segment)
            })

        # 后处理：合并以标点开头的段到前一段
        merged_segments = self._merge_punct_start_segments(segments)

        # 添加序号
        for i, seg in enumerate(merged_segments, 1):
            seg['index'] = i

        return merged_segments

    def _merge_punct_start_segments(self, segments: List[Dict]) -> List[Dict]:
        """后处理：合并以标点开头的段到前一段"""
        merged_segments = []

        for seg in segments:
            if seg['text'] and seg['text'][0] in self.all_punct and merged_segments:
                # 将当前段（去掉开头的标点）附加到前一段
                punct = seg['text'][0]
                remaining_text = seg['text'][1:]

                # 前一段加上标点
                merged_segments[-1]['text'] += punct
                merged_segments[-1]['length'] += 1

                # 如果有剩余内容，作为新段
                if remaining_text:
                    merged_segments.append({
                        'text': remaining_text,
                        'length': len(remaining_text)
                    })
            else:
                merged_segments.append(seg)

        return merged_segments

    def validate_segments(self, segments: List[Dict]) -> List[str]:
        """
        验证分段结果

        Args:
            segments: 分段列表

        Returns:
            问题列表，如果没有问题返回空列表
        """
        issues = []

        for seg in segments:
            # 检查是否以标点开头
            if seg['text'] and seg['text'][0] in self.all_punct:
                issues.append(f"第{seg.get('index', '?')}段以标点开头: {seg['text']}")

            # 检查是否超长
            if seg['length'] > self.max_chars:
                issues.append(f"第{seg.get('index', '?')}段超长({seg['length']}字): {seg['text']}")

        return issues


class SubtitleGenerator:
    """字幕生成器 - 基于 Whisper 和口播稿生成 SRT 字幕"""

    def __init__(self, model_size: str = "base"):
        """
        初始化字幕生成器

        Args:
            model_size: Whisper 模型大小 (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.segmenter = ScriptSegmenter(min_chars=10, max_chars=15)

    def generate_srt(self, audio_path: str, script_text: str) -> str:
        """
        生成 SRT 字幕文件

        Args:
            audio_path: 音频文件路径
            script_text: 口播稿文本

        Returns:
            SRT 格式的字幕内容
        """
        import whisper

        print(f"[字幕生成] 使用 Whisper {self.model_size} 模型...")
        model = whisper.load_model(self.model_size)

        print(f"[字幕生成] 转录音频: {audio_path}")
        result = model.transcribe(
            audio_path,
            language="zh",
            word_timestamps=True,
            verbose=False
        )

        segments = result.get('segments', [])
        if not segments:
            print("[字幕生成] 错误：Whisper 未识别到任何语音")
            return ""

        print(f"[字幕生成] Whisper 识别到 {len(segments)} 个片段")

        # 提取字符级时间戳
        char_timestamps = self._extract_char_timestamps(segments)
        print(f"[字幕生成] 提取到 {len(char_timestamps)} 个字符级时间戳")

        # 对口播稿进行分段
        script_segments = self.segmenter.segment(script_text)
        print(f"[字幕生成] 口播稿分段完成，共 {len(script_segments)} 段")

        # 对齐口播稿和字符级时间戳
        subtitle_entries = self._align_segments_with_timestamps(
            script_segments, char_timestamps
        )
        print(f"[字幕生成] 对齐完成，生成 {len(subtitle_entries)} 个字幕条目")

        # 生成 SRT 内容
        return self._generate_srt_content(subtitle_entries)

    def _extract_char_timestamps(self, whisper_segments: List[Dict]) -> List[Dict]:
        """
        从 Whisper 结果中提取字符级时间戳

        Args:
            whisper_segments: Whisper 识别的片段列表

        Returns:
            字符级时间戳列表
        """
        char_timestamps = []

        for segment in whisper_segments:
            if 'words' in segment:
                for word in segment['words']:
                    word_text = word['word'].strip()
                    word_start = word['start']
                    word_end = word['end']
                    word_duration = word_end - word_start

                    # 将每个字分配到时间戳
                    if len(word_text) > 0:
                        char_duration = word_duration / len(word_text)
                        for i, char in enumerate(word_text):
                            char_timestamps.append({
                                'char': char,
                                'start': word_start + i * char_duration,
                                'end': word_start + (i + 1) * char_duration
                            })

        return char_timestamps

    def _align_segments_with_timestamps(
        self,
        script_segments: List[Dict],
        char_timestamps: List[Dict]
    ) -> List[Dict]:
        """
        将分段后的口播稿与字符级时间戳对齐

        Args:
            script_segments: 分段后的口播稿
            char_timestamps: 字符级时间戳

        Returns:
            字幕条目列表
        """
        # 构建口播稿完整文本
        full_script = ''.join([seg['text'] for seg in script_segments])

        # 构建逐字版完整文本
        full_chars = ''.join([ts['char'] for ts in char_timestamps])

        # 使用 SequenceMatcher 进行对齐
        matcher = SequenceMatcher(None, full_chars, full_script)

        # 创建字符到时间戳的映射
        char_to_timestamp = {i: ts for i, ts in enumerate(char_timestamps)}

        # 对齐后的字幕条目
        subtitle_entries = []
        script_char_index = 0

        for seg in script_segments:
            seg_text = seg['text']
            seg_length = len(seg_text)

            # 找到这段文字对应的字符级时间戳
            start_time = None
            end_time = None

            # 在 char_timestamps 中查找匹配
            for i in range(len(char_timestamps) - seg_length + 1):
                match_text = ''.join([char_timestamps[i + j]['char'] for j in range(seg_length)])
                if match_text == seg_text:
                    start_time = char_timestamps[i]['start']
                    end_time = char_timestamps[i + seg_length - 1]['end']
                    break

            # 如果没找到精确匹配，使用比例估算
            if start_time is None:
                ratio = script_char_index / len(full_script) if full_script else 0
                total_duration = char_timestamps[-1]['end'] if char_timestamps else 0
                start_time = ratio * total_duration
                end_time = start_time + seg_length * 0.2  # 估算每字0.2秒

            subtitle_entries.append({
                'index': seg['index'],
                'start': start_time,
                'end': end_time,
                'text': seg_text
            })

            script_char_index += seg_length

        return subtitle_entries

    def _generate_srt_content(self, subtitle_entries: List[Dict]) -> str:
        """
        生成 SRT 格式的字幕内容

        Args:
            subtitle_entries: 字幕条目列表

        Returns:
            SRT 格式的字幕内容
        """
        lines = []

        for entry in subtitle_entries:
            lines.append(str(entry['index']))
            lines.append(f"{self._format_time(entry['start'])} --> {self._format_time(entry['end'])}")
            lines.append(entry['text'])
            lines.append("")

        return "\n".join(lines)

    def _format_time(self, seconds: float) -> str:
        """
        将秒数格式化为 SRT 时间格式

        Args:
            seconds: 秒数

        Returns:
            SRT 时间格式字符串 (HH:MM:SS,mmm)
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_srt_from_audio(audio_path: str, script_text: str, model_size: str = "base", output_path: str = None) -> str:
    """
    从音频和口播稿生成 SRT 字幕文件

    Args:
        audio_path: MP3 音频文件路径
        script_text: 原始演讲稿（用于替换 Whisper 识别的文字）
        model_size: Whisper 模型大小 (tiny, base, small, medium, large)
        output_path: 输出文件路径，如果为 None 则返回字幕内容

    Returns:
        SRT 格式的字幕内容，或保存到文件返回文件路径
    """
    if not script_text or not script_text.strip():
        print("[字幕生成] 错误：未提供口播稿")
        return ""

    if not os.path.exists(audio_path):
        print(f"[字幕生成] 错误：音频文件不存在: {audio_path}")
        return ""

    try:
        generator = SubtitleGenerator(model_size=model_size)
        srt_content = generator.generate_srt(audio_path, script_text)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            print(f"[字幕生成] 字幕已保存到: {output_path}")
            return output_path

        return srt_content
    except Exception as e:
        print(f"[字幕生成] 错误: {e}")
        import traceback
        traceback.print_exc()
        return ""


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='字幕生成器 - 基于音频和口播稿生成 SRT 字幕')
    parser.add_argument('audio', help='音频文件路径 (MP3/WAV等)')
    parser.add_argument('script', help='口播稿文本文件路径 或直接输入文本')
    parser.add_argument('-o', '--output', help='输出 SRT 文件路径', default=None)
    parser.add_argument('-m', '--model', help='Whisper 模型大小 (tiny/base/small/medium/large)', default='base')
    parser.add_argument('--is-file', action='store_true', help='script 参数是否为文件路径')

    args = parser.parse_args()

    # 获取口播稿内容
    if args.is_file or os.path.exists(args.script):
        with open(args.script, 'r', encoding='utf-8') as f:
            script_text = f.read()
    else:
        script_text = args.script

    # 生成字幕
    result = generate_srt_from_audio(
        audio_path=args.audio,
        script_text=script_text,
        model_size=args.model,
        output_path=args.output
    )

    if result and not args.output:
        print(result)


if __name__ == '__main__':
    main()
