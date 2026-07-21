/**
 * 代码块样式渲染函数
 * 用于将代码块文本转换为带有语法高亮的HTML内容
 */
export const highlightCodeBlock = (htmlContent: string): string => {
  if (!htmlContent || typeof htmlContent !== 'string') return htmlContent;

  // 匹配<pre><code>标签及其内容，支持带有属性的标签
  const codeBlockRegex = /<pre\s*[^>]*><code\s*[^>]*>([\s\S]*?)<\/code><\/pre>/g;

  // 替换所有的<pre><code>块
  return htmlContent.replace(codeBlockRegex, (match, codeContent) => {
    // 后端返回的HTML已经是转义后的，不需要再次转义
    // 直接对原始内容应用语法高亮
    const highlightedCode = applySyntaxHighlight(codeContent);

    // 返回带高亮的代码块
    return `<pre><code>${highlightedCode}</code></pre>`;
  });
};

/**
 * 转义HTML特殊字符
 */
const escapeHtml = (text: string): string => {
  if (!text) return '';
  
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, (m) => map[m] || m);
};

/**
 * 应用语法高亮
 */
const applySyntaxHighlight = (codeContent: string): string => {
  if (!codeContent) return '';
  
  // 分割代码为行
  const lines = codeContent.split('\n');
  const highlightedLines: string[] = [];
  let inBlockComment = false;
  
  // 逐行处理代码
  for (const currentLine of lines) {
    let processedLine = '';
    let j = 0;
    
    while (j < currentLine.length) {
      // 检查块注释 /* */
      if (currentLine.substring(j, j + 2) === '/*' && !inBlockComment) {
        inBlockComment = true;
        const blockCommentEnd = currentLine.indexOf('*/', j + 2);
        if (blockCommentEnd !== -1) {
          processedLine += wrapWithClass(currentLine.substring(j, blockCommentEnd + 2), 'hljs-comment');
          j = blockCommentEnd + 2;
          inBlockComment = false;
        } else {
          processedLine += wrapWithClass(currentLine.substring(j), 'hljs-comment');
          break;
        }
        continue;
      }
      
      // 如果在块注释中
      if (inBlockComment) {
        const blockCommentEnd = currentLine.indexOf('*/', j);
        if (blockCommentEnd !== -1) {
          processedLine += wrapWithClass(currentLine.substring(j, blockCommentEnd + 2), 'hljs-comment');
          j = blockCommentEnd + 2;
          inBlockComment = false;
        } else {
          processedLine += wrapWithClass(currentLine.substring(j), 'hljs-comment');
          break;
        }
        continue;
      }
      
      // 检查行注释 // - 避免将URL中的://识别为注释
      if (currentLine.substring(j, j + 2) === '//' && (j === 0 || currentLine[j - 1] !== ':')) {
        processedLine += wrapWithClass(currentLine.substring(j), 'hljs-comment');
        break;
      }
      
      // 检查行注释 # - 改进匹配规则，支持更多情况
      if (currentLine[j] === '#' && (j === 0 || !/\w/.test(currentLine[j - 1]))) {
        processedLine += wrapWithClass(currentLine.substring(j), 'hljs-comment');
        break;
      }
      
      // 检查HTML注释 <!-- -->
      if (currentLine.substring(j, j + 4) === '<!--') {
        const htmlCommentEnd = currentLine.indexOf('-->', j + 4);
        if (htmlCommentEnd !== -1) {
          processedLine += wrapWithClass(currentLine.substring(j, htmlCommentEnd + 3), 'hljs-comment');
          j = htmlCommentEnd + 3;
        } else {
          processedLine += wrapWithClass(currentLine.substring(j), 'hljs-comment');
          break;
        }
        continue;
      }
      
      // 检查字符串 "..."
      if (currentLine[j] === '"') {
        const stringEnd = findStringEnd(currentLine, j, '"');
        if (stringEnd !== -1) {
          processedLine += wrapWithClass(currentLine.substring(j, stringEnd + 1), 'hljs-string');
          j = stringEnd + 1;
        } else {
          processedLine += wrapWithClass(currentLine.substring(j), 'hljs-string');
          break;
        }
        continue;
      }
      
      // 检查字符串 '...'
      if (currentLine[j] === "'") {
        const stringEnd = findStringEnd(currentLine, j, "'");
        if (stringEnd !== -1) {
          processedLine += wrapWithClass(currentLine.substring(j, stringEnd + 1), 'hljs-string');
          j = stringEnd + 1;
        } else {
          processedLine += wrapWithClass(currentLine.substring(j), 'hljs-string');
          break;
        }
        continue;
      }
      
      // 检查关键字
      const keywordMatch = matchKeyword(currentLine, j);
      if (keywordMatch) {
        processedLine += wrapWithClass(keywordMatch, 'hljs-keyword');
        j += keywordMatch.length;
        continue;
      }
      
      // 检查变量（=左侧）
      const variableMatch = matchVariable(currentLine, j);
      if (variableMatch) {
        processedLine += wrapWithClass(variableMatch, 'hljs-variable');
        j += variableMatch.length;
        continue;
      }
      
      // 检查数字
      const numberMatch = matchNumber(currentLine, j);
      if (numberMatch) {
        processedLine += wrapWithClass(numberMatch, 'hljs-number');
        j += numberMatch.length;
        continue;
      }
      
      // 检查类名（通常是大写开头的标识符）
      const classNameMatch = matchClassName(currentLine, j);
      if (classNameMatch) {
        processedLine += wrapWithClass(classNameMatch, 'hljs-title');
        j += classNameMatch.length;
        continue;
      }
      
      // 普通字符
      processedLine += currentLine[j];
      j++;
    }
    
    highlightedLines.push(processedLine);
  }
  
  return highlightedLines.join('\n');
};

/**
 * 用指定的class包裹文本
 */
const wrapWithClass = (text: string, className: string): string => {
  // 文件已经在 highlightCodeBlock 开始时统一转义过了，这里不需要再次转义
  return `<span class="${className}">${text}</span>`;
};

/**
 * 查找字符串的结束位置（考虑转义字符）
 */
const findStringEnd = (line: string, start: number, quote: string): number => {
  if (!line || start >= line.length) return -1;
  
  for (let i = start + 1; i < line.length; i++) {
    // 跳过转义字符
    if (line[i] === '\\' && i + 1 < line.length) {
      i++;
      continue;
    }
    if (line[i] === quote) {
      return i;
    }
  }
  return -1;
};

/**
 * 匹配常见的编程语言关键字
 */
const matchKeyword = (line: string, start: number): string | null => {
  if (!line || start >= line.length) return null;
  
  // 使用Set去除重复的关键字
  const keywordsSet = new Set([
    'def', 'class', 'if', 'else', 'elif', 'for', 'while', 'in', 'not', 'and', 'or',
    'from', 'import', 'as', 'return', 'yield', 'try', 'except', 'finally', 'with',
    'break', 'continue', 'pass', 'raise', 'assert', 'lambda', 'global', 'nonlocal',
    'True', 'False', 'None', 'public', 'private', 'protected', 'function', 'var',
    'let', 'const', 'typeof', 'instanceof', 'new', 'delete', 'switch', 'case', 'default',
    'do', 'catch', 'throw', 'extends', 'implements', 'interface', 'static', 'final',
    'abstract', 'enum'
  ]);
  
  const keywords = Array.from(keywordsSet);
  
  // 查找可能的关键字
  for (const keyword of keywords) {
    if (line.substring(start, start + keyword.length) === keyword) {
      // 确保是一个完整的单词
      const nextChar = start + keyword.length < line.length ? line[start + keyword.length] : ' ';
      const prevChar = start > 0 ? line[start - 1] : ' ';
      if (!/\w/.test(nextChar) && !/\w/.test(prevChar)) {
        return keyword;
      }
    }
  }
  
  return null;
};

/**
 * 匹配变量（=左侧的标识符）
 */
const matchVariable = (line: string, start: number): string | null => {
  if (!line || start >= line.length) return null;
  
  // 查找等号
  const equalsIndex = line.indexOf('=', start);
  if (equalsIndex === -1 || equalsIndex <= start) {
    return null;
  }
  
  // 提取等号左侧的内容
  const leftSide = line.substring(start, equalsIndex).trim();
  
  // 检查左侧是否是一个有效的变量名（字母、数字、下划线）
  if (/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(leftSide)) {
    // 确保变量名不是关键字
    const keywords = ['if', 'else', 'for', 'while', 'def', 'class', 'import', 'from'];
    if (!keywords.includes(leftSide.toLowerCase())) {
      // 确保左侧没有其他运算符
      if (!leftSide.includes('+') && !leftSide.includes('-') && !leftSide.includes('*') && !leftSide.includes('/')) {
        return leftSide;
      }
    }
  }
  
  return null;
};

/**
 * 匹配数字
 */
const matchNumber = (line: string, start: number): string | null => {
  if (!line || start >= line.length) return null;
  
  const numberRegex = /^\d+(\.\d+)?([eE][+-]?\d+)?/;
  const match = numberRegex.exec(line.substring(start));
  return match ? match[0] : null;
};

/**
 * 匹配类名（大写开头的标识符）
 */
const matchClassName = (line: string, start: number): string | null => {
  if (!line || start >= line.length) return null;
  
  const classNameRegex = /^[A-Z][a-zA-Z0-9_]*/;
  const match = classNameRegex.exec(line.substring(start));
  
  if (match) {
    const className = match[0];
    const nextPos = start + className.length;
    
    // 检查后面是否有点号、括号或空格，增加匹配的准确性
    if (nextPos >= line.length || line[nextPos] === '.' || line[nextPos] === '(' || line[nextPos] === '<' || /\s/.test(line[nextPos])) {
      return className;
    }
  }
  
  return null;
};