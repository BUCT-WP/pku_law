import asyncio
from playwright.async_api import async_playwright
import json
from bs4 import BeautifulSoup
import re
import random
import os

def clean_text_content(text):
    """
    清理文本内容，改善换行逻辑并去除不需要的内容
    """
    if not text:
        return ""
    
    # 去除"法宝新AI"相关内容
    text = re.sub(r'法宝新AI\s*', '', text)
    
    # 处理换行逻辑
    lines = text.split('\n')
    cleaned_lines = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:  # 跳过空行
            continue
            
        # 如果当前行很短（可能是被错误分割的），且下一行存在，尝试合并
        if (len(line) < 20 and i + 1 < len(lines) and 
            lines[i + 1].strip() and 
            not line.endswith(('。', '；', '：', '、', '！', '？', '"', '"', '》', '）'))):
            # 检查是否应该合并到上一行
            if cleaned_lines and not cleaned_lines[-1].endswith(('。', '；', '：', '！', '？', '"', '"', '》')):
                cleaned_lines[-1] += line
            else:
                cleaned_lines.append(line)
        else:
            # 如果上一行很短且当前行不是标题或编号，尝试合并到上一行
            if (cleaned_lines and len(cleaned_lines[-1]) < 20 and 
                not re.match(r'^[一二三四五六七八九十\d]+[、．]', line) and
                not re.match(r'^第[一二三四五六七八九十\d]+条', line) and
                not re.match(r'^第[一二三四五六七八九十\d]+章', line)):
                cleaned_lines[-1] += line
            else:
                cleaned_lines.append(line)
    
    # 合并后再次处理，确保段落完整性
    final_lines = []
    i = 0
    while i < len(cleaned_lines):
        current_line = cleaned_lines[i]
        
        # 检查是否需要与下一行合并
        while (i + 1 < len(cleaned_lines) and 
               not current_line.endswith(('。', '；', '！', '？', '"', '"', '》')) and
               not re.match(r'^[一二三四五六七八九十\d]+[、．]', cleaned_lines[i + 1]) and
               not re.match(r'^第[一二三四五六七八九十\d]+[条章]', cleaned_lines[i + 1])):
            i += 1
            if i < len(cleaned_lines):
                current_line += cleaned_lines[i]
        
        final_lines.append(current_line)
        i += 1
    
    # 重新组织文本，确保适当的段落分隔
    result = []
    for line in final_lines:
        if line.strip():
            result.append(line.strip())
    
    return '\n'.join(result)

async def get_page_response(url):
    """
    使用Playwright获取指定URL的响应
    """
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=True)
        
        # 创建新页面
        page = await browser.new_page()
        
        # 设置完整的请求头，模拟真实浏览器
        await page.set_extra_http_headers({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Cookie': 'referer=https://www.pkulaw.com/chl/2a002e408a3b3827bdfb.html; CookieId=0cce6def6e9471542b9375e01f6ae1f9; SUB=a4e77e87-4f16-4911-b968-47c4b8a36245; preferred_username=%E5%8C%97%E4%BA%AC%E5%8C%96%E5%B7%A5%E5%A4%A7%E5%AD%A6; loginType=ip; session_state=0f449870-da38-4bb2-b489-9950c6225e80; xCloseNew=2; _bl_uid=Fzmjtct6jCet7dxXw1n8eastsO0F; pkulaw_v6_sessionid=aay1kpuydp5emqoow2z5l4cw; Hm_lvt_8266968662c086f34b2a3e2ae9014bf8=1751332003,1751339146,1751369195; HMACCOUNT=C9000E37F559039A; cookieUUID=cookieUUID_1751369195747; userislogincookie=always; LoginAccount=%e5%8c%97%e4%ba%ac%e5%8c%96%e5%b7%a5%e5%a4%a7%e5%ad%a6; UserAuthAssetAid=; authormes=b31681372881bca73e55f754376488ab3655642886719161605a2f1b2075ef9335b7d5e9345c01a9bdfb; Hm_lpvt_8266968662c086f34b2a3e2ae9014bf8=1751369198; Hm_up_8266968662c086f34b2a3e2ae9014bf8=%7B%22ysx_yhqx_20220602%22%3A%7B%22value%22%3A%220%22%2C%22scope%22%3A1%7D%2C%22ysx_hy_20220527%22%3A%7B%22value%22%3A%2201%22%2C%22scope%22%3A1%7D%2C%22uid_%22%3A%7B%22value%22%3A%225f634e21-d5b1-ed11-b393-00155d3c0709%22%2C%22scope%22%3A1%7D%2C%22ysx_yhjs_20220602%22%3A%7B%22value%22%3A%222%22%2C%22scope%22%3A1%7D%7D',
            'Referer': 'https://www.pkulaw.com/chl/2a002e408a3b3827bdfb.html',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"'
        })
        
        try:
            # 访问页面
            response = await page.goto(url, wait_until='networkidle')
            
            # 获取响应信息
            response_data = {
                'url': response.url,
                'status': response.status,
                'status_text': response.status_text,
                'headers': dict(response.headers),
                'content': await page.content(),
                'title': await page.title()
            }
            
            # print(f"状态码: {response.status}")
            # print(f"页面标题: {await page.title()}")
            # print(f"响应URL: {response.url}")
            # print(f"响应头: {json.dumps(dict(response.headers), indent=2, ensure_ascii=False)}")
            # print(f"页面内容长度: {len(await page.content())} 字符")
            
            # 获取完整页面内容
            page_content = await page.content()
            
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # 创建law文件夹（如果不存在）
            law_folder = "law"
            if not os.path.exists(law_folder):
                os.makedirs(law_folder)
                print(f"创建文件夹: {law_folder}")
            
            # 查找class=title的元素作为文件名
            title_element = soup.find('h2', class_='title')
            if title_element:
                title_text = title_element.get_text(strip=True)
                # 清理文件名，移除不允许的字符
                import re
                safe_filename = re.sub(r'[<>:"/\\|?*]', '_', title_text)
                safe_filename = safe_filename.strip()[:100]  # 限制长度
                filename = os.path.join(law_folder, f"{safe_filename}.txt")
            else:
                filename = os.path.join(law_folder, "divFullText_content.txt")
                print("未找到class='title'的元素，使用默认文件名")
            
            # 查找id为divFullText的div元素
            div_full_text = soup.find('div', id='divFullText')
            
            if div_full_text:
                # 移除不需要的元素（如"法宝新AI"相关的元素）
                # 查找并移除包含"法宝新AI"的元素
                for element in div_full_text.find_all(text=lambda text: text and "法宝新AI" in text):
                    element.extract()
                
                # 移除可能包含广告或无关内容的特定标签
                for tag in div_full_text.find_all(['script', 'style', 'iframe']):
                    tag.decompose()
                
                # 移除包含"法宝新AI"的父元素
                for element in div_full_text.find_all():
                    if element.get_text(strip=True) == "法宝新AI":
                        element.decompose()
                
                # 获取div元素的纯文本内容
                div_text_content = div_full_text.get_text(separator='\n', strip=True)
                
                # 清理文本内容
                cleaned_content = clean_text_content(div_text_content)
                
                # 保存清理后的文本内容到law文件夹
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)
                print(f"divFullText纯文本内容已保存到 {filename}")
                
                # 打印一些基本信息
                print(f"divFullText文本长度: {len(cleaned_content)} 字符")
                
                # 打印内容预览
                preview = cleaned_content[:200] + "..." if len(cleaned_content) > 200 else cleaned_content
                print(f"内容预览: {preview}")
                
            else:
                print("未找到id为divFullText的元素")
                # 打印页面中所有div元素的id，帮助调试
                all_divs = soup.find_all('div', id=True)
                print("页面中发现的div元素id:")
                for div in all_divs[:10]:  # 只显示前10个
                    print(f"  - {div.get('id')}")
            
            return response_data
            
        except Exception as e:
            print(f"获取页面时出错: {e}")
            return None
        finally:
            # 关闭浏览器
            await browser.close()

async def process_urls_from_file(file_path):
    """
    从文件中读取URL并逐个处理，处理完一个删除一个
    """
    urls_file = os.path.abspath(file_path)
    
    if not os.path.exists(urls_file):
        print(f"文件 {urls_file} 不存在")
        return
    
    total_processed = 0
    
    while True:
        # 读取当前文件中的所有URL
        try:
            with open(urls_file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f.readlines() if line.strip()]
        except Exception as e:
            print(f"读取URLs文件时出错: {e}")
            break
        
        # 如果没有URL了，结束处理
        if not urls:
            print("所有URL已处理完成！")
            break
        
        # 取第一个URL进行处理
        current_url = urls[0]
        remaining_urls = urls[1:]
        
        print(f"\n{'='*60}")
        print(f"正在处理第 {total_processed + 1} 个URL")
        print(f"剩余URL数量: {len(remaining_urls)}")
        print(f"当前URL: {current_url}")
        print(f"{'='*60}")
        
        # 处理当前URL
        response_data = await get_page_response(current_url)
        
        if response_data:
            print(f"✅ URL处理成功: {current_url}")
        else:
            print(f"❌ URL处理失败: {current_url}")
        
        # 更新文件，移除已处理的URL
        try:
            with open(urls_file, 'w', encoding='utf-8') as f:
                for url in remaining_urls:
                    f.write(url + '\n')
            print(f"已从文件中移除处理完的URL")
        except Exception as e:
            print(f"更新URLs文件时出错: {e}")
        
        total_processed += 1
        
        # 如果还有剩余URL，等待随机间隔
        if remaining_urls:
            wait_time = random.uniform(1, 5)
            print(f"等待 {wait_time:.1f} 秒后处理下一个URL...")
            await asyncio.sleep(wait_time)
    
    print(f"\n🎉 批量处理完成！总共处理了 {total_processed} 个URL")

async def main():
    urls_file = "urls.txt"
    print(f"开始批量处理URL文件: {urls_file}")
    
    await process_urls_from_file(urls_file)

if __name__ == "__main__":
    asyncio.run(main())