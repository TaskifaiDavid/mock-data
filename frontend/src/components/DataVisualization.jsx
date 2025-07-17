import React, { useState } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
} from 'chart.js'
import { Bar, Line, Pie, Doughnut } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement
)

const DataVisualization = ({ results, sqlQuery, originalMessage }) => {
  const [viewMode, setViewMode] = useState('auto') // auto, table, chart
  const [chartType, setChartType] = useState('bar') // bar, line, pie, doughnut
  
  if (!results || results.length === 0) {
    return null
  }

  // Analyze data structure to determine best visualization
  const analyzeDataForVisualization = () => {
    if (results.length === 0) return null
    
    const firstRow = results[0]
    const columns = Object.keys(firstRow)
    const numericColumns = columns.filter(col => {
      return results.some(row => 
        row[col] !== null && 
        row[col] !== undefined && 
        !isNaN(Number(row[col])) &&
        Number(row[col]) !== 0
      )
    })
    
    const textColumns = columns.filter(col => 
      !numericColumns.includes(col) && 
      typeof firstRow[col] === 'string'
    )
    
    return {
      columns,
      numericColumns,
      textColumns,
      hasNumericData: numericColumns.length > 0,
      hasCategories: textColumns.length > 0,
      rowCount: results.length,
      suggestedChart: getSuggestedChartType(results, numericColumns, textColumns)
    }
  }

  const getSuggestedChartType = (data, numericCols, textCols) => {
    // Time series data (has year/month)
    if (textCols.some(col => col.includes('quarter')) || 
        numericCols.some(col => col.includes('year') || col.includes('month'))) {
      return 'line'
    }
    
    // Few categories with one main metric
    if (data.length <= 10 && textCols.length === 1 && numericCols.length >= 1) {
      return 'pie'
    }
    
    // Multiple categories or metrics
    if (textCols.length > 0 && numericCols.length > 0) {
      return 'bar'
    }
    
    return 'bar'
  }

  const createChartData = (type) => {
    const analysis = analyzeDataForVisualization()
    if (!analysis.hasNumericData || !analysis.hasCategories) {
      return null
    }

    const labelColumn = analysis.textColumns[0] // First text column as labels
    const valueColumns = analysis.numericColumns.slice(0, 3) // Up to 3 numeric columns
    
    const labels = results.map(row => String(row[labelColumn] || 'Unknown'))
    
    if (type === 'pie' || type === 'doughnut') {
      // Use only first numeric column for pie charts
      const values = results.map(row => Number(row[valueColumns[0]]) || 0)
      
      return {
        labels,
        datasets: [{
          data: values,
          backgroundColor: [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
            '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
          ],
          borderWidth: 1
        }]
      }
    } else {
      // Bar and line charts can handle multiple series
      const datasets = valueColumns.map((col, index) => {
        const values = results.map(row => Number(row[col]) || 0)
        const colors = ['#36A2EB', '#FF6384', '#FFCE56', '#4BC0C0', '#9966FF']
        
        return {
          label: col.replace(/_/g, ' ').toUpperCase(),
          data: values,
          backgroundColor: type === 'line' ? 'transparent' : colors[index % colors.length],
          borderColor: colors[index % colors.length],
          borderWidth: 2,
          fill: false
        }
      })
      
      return { labels, datasets }
    }
  }

  const getChartOptions = (type) => {
    const analysis = analyzeDataForVisualization()
    
    const baseOptions = {
      responsive: true,
      plugins: {
        legend: {
          position: 'top',
        },
        title: {
          display: true,
          text: getChartTitle()
        }
      }
    }

    if (type === 'pie' || type === 'doughnut') {
      return {
        ...baseOptions,
        plugins: {
          ...baseOptions.plugins,
          legend: {
            position: 'right',
          }
        }
      }
    }

    return {
      ...baseOptions,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function(value) {
              // Format large numbers
              if (value >= 1000000) {
                return (value / 1000000).toFixed(1) + 'M'
              } else if (value >= 1000) {
                return (value / 1000).toFixed(1) + 'K'
              }
              return value
            }
          }
        },
        x: {
          ticks: {
            maxRotation: 45,
            minRotation: 0
          }
        }
      }
    }
  }

  const getChartTitle = () => {
    const message = originalMessage?.toLowerCase() || ''
    
    if (message.includes('top') || message.includes('best')) {
      return 'Top Performance Analysis'
    } else if (message.includes('trend') || message.includes('time') || message.includes('month')) {
      return 'Trend Analysis Over Time'
    } else if (message.includes('compare') || message.includes('vs')) {
      return 'Comparison Analysis'
    } else if (message.includes('product')) {
      return 'Product Performance'
    } else if (message.includes('reseller') || message.includes('customer')) {
      return 'Customer/Reseller Analysis'
    }
    
    return 'Data Analysis'
  }

  const exportToCSV = () => {
    if (!results || results.length === 0) return
    
    const columns = Object.keys(results[0])
    const csvContent = [
      columns.join(','),
      ...results.map(row => 
        columns.map(col => {
          const value = row[col]
          // Escape commas and quotes in CSV
          if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
            return `"${value.replace(/"/g, '""')}"`
          }
          return value
        }).join(',')
      )
    ].join('\n')
    
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `query_results_${new Date().toISOString().slice(0, 10)}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  }

  const analysis = analyzeDataForVisualization()
  const chartData = createChartData(chartType)
  const canVisualize = analysis && analysis.hasNumericData && analysis.hasCategories
  
  const shouldAutoShowChart = () => {
    if (!canVisualize) return false
    
    // Auto-show charts for certain query types
    const message = originalMessage?.toLowerCase() || ''
    return (
      message.includes('top') || 
      message.includes('best') || 
      message.includes('trend') || 
      message.includes('compare') ||
      message.includes('breakdown') ||
      results.length <= 20 // Small result sets
    )
  }

  const effectiveViewMode = viewMode === 'auto' ? 
    (shouldAutoShowChart() ? 'chart' : 'table') : viewMode

  const renderChart = () => {
    if (!chartData) return <div>Cannot create chart from this data</div>
    
    const ChartComponent = {
      bar: Bar,
      line: Line,
      pie: Pie,
      doughnut: Doughnut
    }[chartType]
    
    return (
      <div className="chart-container">
        <ChartComponent data={chartData} options={getChartOptions(chartType)} />
      </div>
    )
  }

  const renderTable = () => {
    const displayResults = results.slice(0, 50) // Show max 50 rows
    const columns = Object.keys(displayResults[0])

    return (
      <div className="results-table">
        <table>
          <thead>
            <tr>
              {columns.map(col => (
                <th key={col}>{col.replace(/_/g, ' ').toUpperCase()}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {displayResults.map((row, index) => (
              <tr key={index}>
                {columns.map(col => (
                  <td key={col}>
                    {row[col] !== null && row[col] !== undefined 
                      ? String(row[col]) 
                      : '-'
                    }
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        {results.length > 50 && (
          <div className="table-note">
            Showing first 50 of {results.length} results
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="data-visualization">
      <div className="visualization-header">
        <div className="view-controls">
          <span className="results-count">
            📊 {results.length} results
          </span>
          
          <div className="view-buttons">
            <button 
              className={effectiveViewMode === 'table' ? 'active' : ''}
              onClick={() => setViewMode('table')}
            >
              📋 Table
            </button>
            
            {canVisualize && (
              <button 
                className={effectiveViewMode === 'chart' ? 'active' : ''}
                onClick={() => setViewMode('chart')}
              >
                📈 Chart
              </button>
            )}
            
            <button onClick={exportToCSV} className="export-btn">
              💾 Export CSV
            </button>
          </div>
        </div>
        
        {effectiveViewMode === 'chart' && canVisualize && (
          <div className="chart-controls">
            <label>Chart Type:</label>
            <select 
              value={chartType} 
              onChange={(e) => setChartType(e.target.value)}
            >
              <option value="bar">📊 Bar Chart</option>
              <option value="line">📈 Line Chart</option>
              <option value="pie">🥧 Pie Chart</option>
              <option value="doughnut">🍩 Doughnut Chart</option>
            </select>
          </div>
        )}
      </div>

      <div className="visualization-content">
        {effectiveViewMode === 'chart' && canVisualize ? renderChart() : renderTable()}
      </div>
      
      {canVisualize && analysis && (
        <div className="data-insights">
          <small>
            💡 Found {analysis.numericColumns.length} numeric columns and {analysis.textColumns.length} category columns
            {analysis.suggestedChart && ` • Suggested: ${analysis.suggestedChart} chart`}
          </small>
        </div>
      )}
    </div>
  )
}

export default DataVisualization