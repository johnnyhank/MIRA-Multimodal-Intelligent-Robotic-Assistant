from playsound import playsound
import edge_tts as et
import asyncio

async def text_to_speech(text, voice="zh-CN-YunyangNeural", rate="-10%", volume="+10%", pitch="+5Hz"):
    # 合成音频
    communicate = et.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        volume=volume,
        pitch=pitch
    )
    output_file = "temp/output.wav"
    await communicate.save(output_file)

    # 播放音频
    # print(f"正在播放音频：{output_file}")
    playsound(output_file)

if __name__ == '__main__':

    # 示例调用
    text = "你好，这是你的机械臂助手。"
    asyncio.run(text_to_speech(text))
