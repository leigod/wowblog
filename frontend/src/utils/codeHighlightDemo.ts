/**
 * 代码高亮函数使用示例
 */
import { highlightCodeBlock } from './codeHighlight';

// 示例代码块文本
const exampleCodeBlock = `
<pre><code>from sqlalchemy import create_engine, Column, Integer, String 
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.orm import sessionmaker 

# MySQL 数据库连接 URL 
# 格式：mysql+pymysql://用户名:密码@主机:端口/数据库名 
DATABASE_URL = "mysql+pymysql://root:your_password@localhost:3306/test_db" 

# 创建引擎 
engine = create_engine(DATABASE_URL) 

# 创建会话工厂 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 

# 创建 Base 类，用于定义模型 
Base = declarative_base() 

# 定义 User 模型 
class User(Base): 
    __tablename__ = "users" 
    id = Column(Integer, primary_key=True, index=True) 
    name = Column(String(50), index=True)  # MySQL 需要指定字符串长度 
    email = Column(String(100), unique=True, index=True) 

# 创建表（如果表不存在） 
Base.metadata.create_all(bind=engine)</code></pre>
`;

/**
 * 测试代码高亮函数
 */
export const testCodeHighlight = () => {
  try {
    // 应用代码高亮
    const highlightedHtml = highlightCodeBlock(exampleCodeBlock);
    
    // 打印结果到控制台
    console.log('原始代码块:');
    console.log(exampleCodeBlock);
    console.log('\n高亮后的代码块:');
    console.log(highlightedHtml);
    
    return {
      success: true,
      original: exampleCodeBlock,
      highlighted: highlightedHtml
    };
  } catch (error) {
    console.error('代码高亮过程中出错:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : '未知错误'
    };
  }
};

/**
 * 将代码高亮函数集成到文章内容处理中
 */
export const processArticleContent = (articleHtml: string): string => {
  // 处理文章中的所有代码块
  const processedHtml = highlightCodeBlock(articleHtml);
  
  // 可以在这里添加其他文章处理逻辑
  
  return processedHtml;
};