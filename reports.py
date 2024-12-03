import yfinance as yf
from fpdf import FPDF
import gradio as gr
from transformers import pipeline

# Initialize Hugging Face summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Function to fetch stock data
def fetch_stock_data(ticker):
    stock = yf.Ticker(ticker)
    data = stock.info
    return {
        "name": data.get("longName", "N/A"),
        "sector": data.get("sector", "N/A"),
        "price": data.get("currentPrice", "N/A"),
        "market_cap": data.get("marketCap", "N/A"),
        "pe_ratio": data.get("trailingPE", "N/A"),
        "dividend_yield": data.get("dividendYield", "N/A"),
        "summary": data.get("longBusinessSummary", "N/A")
    }

# Function to summarize text using Hugging Face
def summarize_text(text):
    try:
        if len(text) > 0:
            summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
            return summary[0]['summary_text']
        else:
            return "No summary available."
    except Exception as e:
        return f"Error summarizing text: {e}"

# Function to generate PDF report
def generate_pdf_report(ticker, stock_data, summary):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Page 1: Summary
    pdf.cell(200, 10, txt="Investment Report", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt="Company Overview", ln=True, align="L")
    pdf.ln(10)
    pdf.multi_cell(0, 10, f"Name: {stock_data['name']}\n"
                          f"Sector: {stock_data['sector']}\n"
                          f"Price: ${stock_data['price']}\n"
                          f"Market Cap: ${stock_data['market_cap']}\n"
                          f"P/E Ratio: {stock_data['pe_ratio']}\n"
                          f"Dividend Yield: {stock_data['dividend_yield']}%\n")

    # Page 2: Business Summary
    pdf.add_page()
    pdf.cell(200, 10, txt="Business Summary", ln=True, align="L")
    pdf.ln(10)
    pdf.multi_cell(0, 10, summary)

    # Save PDF
    pdf_name = f"{ticker}_report.pdf"
    pdf.output(pdf_name)
    return pdf_name

# Main function for Gradio
def create_report(ticker):
    stock_data = fetch_stock_data(ticker)
    if stock_data["name"] == "N/A":
        return f"Could not fetch data for ticker: {ticker}", None
    
    summary = summarize_text(stock_data['summary'])
    pdf_path = generate_pdf_report(ticker, stock_data, summary)
    return f"Report for {ticker} generated successfully!", pdf_path

# Generate reports for 12 predefined tickers
def batch_generate_reports():
    tickers = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META",
        "NVDA", "JPM", "V", "DIS", "NFLX", "PG"
    ]
    results = []
    for ticker in tickers:
        message, pdf_file = create_report(ticker)
        results.append((ticker, message, pdf_file))
    return results

# Gradio Interface
def generate_report_interface(ticker=None):
    if ticker:
        message, pdf_file = create_report(ticker)
        return message, pdf_file
    else:
        results = batch_generate_reports()
        summary = "\n".join([f"{res[0]}: {res[1]}" for res in results])
        return summary, None

demo = gr.Interface(
    fn=generate_report_interface,
    inputs="text",
    outputs=["text", "file"],
    title="Investment Report Generator",
    description="Enter a stock ticker symbol to generate a single investment report, or leave blank to generate reports for 12 preselected stocks."
)

# Launch the Gradio demo
if __name__ == "__main__":
    demo.launch()
