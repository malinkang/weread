const { Client } = require("@notionhq/client");
const { NotionToMarkdown } = require("notion-to-md");
const fs = require('fs');

// 初始化 Notion 客户端和 NotionToMarkdown
const notion = new Client({ auth: process.env.NOTION_TOKEN });
const n2m = new NotionToMarkdown({ notionClient: notion });

n2m.setCustomTransformer("callout", async (block) => {
  let has_children = block.has_children
  let callout = block.callout;
  let block_id = block.id;
  let emoji;
  let children;
  let text = callout.rich_text[0].text.content;
  if (callout.icon && callout.icon.type === "emoji") {
    emoji = callout.icon.emoji;
  }
  if (has_children) {
    const { results } = await notion.blocks.children.list({
      block_id,
    });
    const mdblocks = await n2m.blocksToMarkdown(results);
    children = n2m.toMarkdownString(mdblocks).parent
  }
  return `!!! note "笔记"\n\n\t ${text} ${children ? "" + children.replace("\n", "\n\t") : ""}`;
});
// 自定义转换器
n2m.setCustomTransformer('heading_1', (block) => {
  const text = block.heading_1.rich_text[0].text.content
  return `## ${text}\n\n`;
});

n2m.setCustomTransformer('heading_2', (block) => {
  const text = block.heading_2.rich_text[0].text.content
  return `### ${text}\n\n`;
});
n2m.setCustomTransformer('heading_3', (block) => {
  const text = block.heading_3.rich_text[0].text.content
  return `#### ${text}\n\n`;
});

function extractPageId(notionUrl) {
  // 正则表达式匹配 32 个字符的 Notion page_id
  const regex = /([a-f0-9]{32}|[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/;
  const match = notionUrl.match(regex);
  if (match) {
    return match[0];
  } else {
    throw new Error("获取NotionID失败，请检查输入的Url是否正确");
  }
}

async function searchDatabase(blockId) {
  const databaseName = process.env.BOOK_DATABASE_NAME || "书架";

  try {
    const response = await notion.blocks.children.list({ block_id: blockId });
    const children = response.results;

    for (const child of children) {
      // 检查当前块是否是数据库且名为"书架"
      if (child.type === "child_database" && child.child_database.title === databaseName) {
        return child.id;
      }
      // 如果当前块有子块，递归搜索
      if (child.has_children) {
        const found = await searchDatabase(child.id);
        // 只有当找到匹配项时才返回
        if (found) return found;
      }
    }
    // 如果遍历完当前层级的所有块都没有找到，返回null
    return null;
  } catch (error) {
    console.error("Error searching database:", error);
    throw error;
  }
}

async function getAllPagesFromDatabase(databaseId, startCursor = null) {
  let hasMore = true;
  let pages = [];
  let nextCursor = startCursor;

  while (hasMore) {
    const queryParameters = {
      database_id: databaseId,
    };
    if (nextCursor) {
      queryParameters.start_cursor = nextCursor;
    }
    const response = await notion.databases.query(queryParameters);



    pages = pages.concat(response.results);

    if (response.has_more) {
      nextCursor = response.next_cursor;
    } else {
      hasMore = false;
    }
  }

  return pages;
}


(async () => {
  try {
    const pageId = extractPageId(process.env.NOTION_PAGE)
    const databaseId = await searchDatabase(pageId)
    const results = await getAllPagesFromDatabase(databaseId);
    console.log("results = " + results.length)
    // 遍历所有页面
    for (const page of results) {
      // 获取页面标题（假设标题是一个文本属性）
      const titleProperty = page.properties['书名']; // 'Name' 是标题属性的名称，可能需要根据实际情况调整
      const pageTitle = titleProperty.title[0].plain_text;

      // 获取关联属性（假设关联属性名为 'Tags'）
      const relationProperty = page.properties['分类'];
      const relationIds = relationProperty.relation.map(rel => rel.id);
      const tags = [];

      // 对于每个关联 ID，获取关联页面的详细信息
      for (const relationId of relationIds) {
        const relatedPage = await notion.pages.retrieve({ page_id: relationId });
        // 假设关联页面的标题属性名为 'Name'
        const relatedPageTitle = relatedPage.properties['标题'].title[0].plain_text;
        tags.push(relatedPageTitle);
      }

      // 使用 pageToMarkdown 转换页面
      const mdblocks = await n2m.pageToMarkdown(page.id);
      const mdString = n2m.toMarkdownString(mdblocks).parent;
      console.log(`mdString = ${mdString}`)
      // 创建 Front Matter
      let frontMatter = `---\ntitle: ${pageTitle}\n`;
      if (tags.length > 0) {
        frontMatter += `tags:\n${tags.map(tag => `  - ${tag}`).join('\n')}\n`;
      }
      frontMatter += '---\n\n';
      const fileProperty = page.properties['封面'];
      let imageUrl = '';
      if (fileProperty && fileProperty.type === 'files' && fileProperty.files.length > 0) {
        // 假设我们只关心第一个文件
        const firstFile = fileProperty.files[0];
        if (firstFile.type === 'file') {
          imageUrl = firstFile.file.url;
        } else if (firstFile.type === 'external') {
          imageUrl = firstFile.external.url;
        }
      }
      frontMatter += `![](${imageUrl})\n\n`;

      // 创建文件名并替换不合法的文件名字符
      const filename = pageTitle.replace(/[<>:"\/\\|?*]+/g, '-') + '.md';

      // 将 Front Matter 和 Markdown 内容写入以页面标题命名的文件
      fs.writeFileSync(`./docs/books/${filename}`, frontMatter + mdString);

      console.log(`Markdown content for page "${pageTitle}" has been written to ${filename}`);
    }
  } catch (error) {
    console.error('Error occurred:', error);
  }
})();