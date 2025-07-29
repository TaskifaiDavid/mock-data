import React from 'react'
import { InlineMath, BlockMath } from 'react-katex'

export const renderMathContent = (content) => {
  if (!content || typeof content !== 'string') {
    return content
  }

  const parts = []
  let lastIndex = 0
  
  // Match display math \[...\] and inline math \(...\)
  const mathRegex = /(\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\))/g
  let match
  
  while ((match = mathRegex.exec(content)) !== null) {
    // Add text before math
    if (match.index > lastIndex) {
      const textBefore = content.slice(lastIndex, match.index)
      if (textBefore) {
        parts.push(textBefore)
      }
    }
    
    const mathExpression = match[1]
    
    if (mathExpression.startsWith('\\[') && mathExpression.endsWith('\\]')) {
      // Display math
      const mathContent = mathExpression.slice(2, -2).trim()
      try {
        parts.push(
          <BlockMath key={`block-${match.index}`} math={mathContent} />
        )
      } catch (error) {
        console.warn('KaTeX error:', error)
        parts.push(mathExpression)
      }
    } else if (mathExpression.startsWith('\\(') && mathExpression.endsWith('\\)')) {
      // Inline math
      const mathContent = mathExpression.slice(2, -2).trim()
      try {
        parts.push(
          <InlineMath key={`inline-${match.index}`} math={mathContent} />
        )
      } catch (error) {
        console.warn('KaTeX error:', error)
        parts.push(mathExpression)
      }
    }
    
    lastIndex = match.index + match[0].length
  }
  
  // Add remaining text
  if (lastIndex < content.length) {
    const remainingText = content.slice(lastIndex)
    if (remainingText) {
      parts.push(remainingText)
    }
  }
  
  // If no math was found, return original content
  if (parts.length === 0) {
    return content
  }
  
  return parts.map((part, index) => 
    React.isValidElement(part) ? part : <span key={`text-${index}`}>{part}</span>
  )
}