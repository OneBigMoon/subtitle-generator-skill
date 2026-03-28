#!/usr/bin/env python3
"""本地测试字幕生成"""

from subtitle_generator import generate_srt_from_audio

# 读取口播稿
with open('input/测试.txt', 'r', encoding='utf-8') as f:
    script_text = f.read()

print('🎬 开始测试字幕生成...')
print(f'📄 口播稿长度: {len(script_text)} 字符')
print(f'🎵 音频文件: input/测试.mp3')
print()

# 生成字幕
srt_content = generate_srt_from_audio(
    audio_path='input/测试.mp3',
    script_text=script_text,
    model_size='base',
    output_path='output/测试_output.srt'
)

if srt_content:
    print()
    print('✅ 字幕生成成功！')
    print(f'📄 字幕长度: {len(srt_content)} 字符')
    print(f'💾 已保存到: output/测试_output.srt')
    print()
    print('📝 生成的字幕内容预览（前500字符）:')
    print('-' * 50)
    print(srt_content[:500])
    print('-' * 50)
else:
    print('❌ 字幕生成失败')
