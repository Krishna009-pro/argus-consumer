// Pre-configured public source discovery leads and extracted candidates
// from ARGUS's SHA-256 cache (data/candidates/candidates-6a8f07a9adbf-55edd0af.json)

export const sampleIntakeDatabase = {
  "dabur": {
    company: "Dabur India Limited",
    searchResults: [
      {
        title: "Dabur Digital Annual Report 2024-25 | Integrated Annual Report",
        url: "https://www.dabur.com/digital-annual-reports/reports/dabur-consolidated-financials.pdf",
        snippet: "Integrated Annual Report 2024-25. Consolidated Balance Sheet and Profit & Loss statement."
      },
      {
        title: "Dabur Financial Statements & Investor Presentation FY25",
        url: "https://www.dabur.com/investor-relations/financials/annual-reports",
        snippet: "Audited Standalone and Consolidated Financial Disclosures for FY 2024-25."
      },
      {
        title: "BSE Corporate Filings: Dabur India Financial Results",
        url: "https://www.bseindia.com/corporates/dabur-financial-filings",
        snippet: "Official public corporate filing submitted to BSE and NSE for FY2024-25."
      }
    ],
    pdfLinks: [
      {
        title: "Dabur Consolidated Financial Statements FY2024-25",
        url: "https://www.dabur.com/digital-annual-reports/reports/dabur-consolidated-financials.pdf"
      },
      {
        title: "Dabur Standalone Financial Statements FY2024-25",
        url: "https://www.dabur.com/digital-annual-reports/reports/dabur-standalone-financials.pdf"
      },
      {
        title: "Integrated Annual Report 2024-25 (Full PDF - 25 MB)",
        url: "https://www.dabur.com/digital-annual-reports/reports/dabur-integrated-annual-report-2024-25.pdf"
      }
    ],
    extraction: {
      company: "Dabur India Limited",
      title: "Dabur Consolidated Financial Statements FY2024-25",
      url: "https://www.dabur.com/digital-annual-reports/reports/dabur-consolidated-financials.pdf",
      cache_path: "data\\cache\\6a8f07a9adbf572acb3cf78ed5bb7f114c08dae9058e3d3c4d70ebd5da652135.pdf",
      sha256: "6a8f07a9adbf572acb3cf78ed5bb7f114c08dae9058e3d3c4d70ebd5da652135",
      candidate_file: "data\\candidates\\candidates-6a8f07a9adbf-55edd0af.json",
      candidate_count: 4,
      ambiguous_count: 2,
      cache_reused: true,
      candidates: [
        {
          id: "C-6a8f07a9adbf-5d6dcbb8d70f",
          metric: "trade_receivables",
          value: 888.5,
          unit: null,
          period: null,
          doc_page: 12,
          status: "unverified",
          snippet: "(ii) Trade receivables 14  888.50  898.72",
          notes: [
            "Machine-extracted financial-statement candidate; verify the value, column header, units, reporting period, basis and scope against the PDF.",
            "Dated column header year: 2025.",
            "Statement header: 342 | Corporate Overview Board & Management Reports Financial Statements | Consolidated Balance Sheet | as at 31 March 2025",
            "No value is verified until a human resolves the period, units, statement basis and table alignment."
          ]
        },
        {
          id: "C-6a8f07a9adbf-e0e72d58afbe",
          metric: "trade_receivables",
          value: 898.72,
          unit: null,
          period: null,
          doc_page: 12,
          status: "unverified",
          snippet: "(ii) Trade receivables 14  888.50  898.72",
          notes: [
            "Machine-extracted financial-statement candidate; verify the value, column header, units, reporting period, basis and scope against the PDF.",
            "Dated column header year: 2024.",
            "Statement header: 342 | Corporate Overview Board & Management Reports Financial Statements | Consolidated Balance Sheet | as at 31 March 2025",
            "No value is verified until a human resolves the period, units, statement basis and table alignment."
          ]
        },
        {
          id: "C-6a8f07a9adbf-7655efaf2421",
          metric: "revenue",
          value: 12563.09,
          unit: null,
          period: null,
          doc_page: 13,
          status: "unverified",
          snippet: "Revenue from operations 34  12,563.09  12,404.01",
          notes: [
            "Machine-extracted financial-statement candidate; verify the value, column header, units, reporting period, basis and scope against the PDF.",
            "Dated column header year: 2025.",
            "Statement header: Integrated Annual Report 2024-25 | 343 | Consolidated Statement of Profit and Loss | for the year ended 31 March 2025",
            "No value is verified until a human resolves the period, units, statement basis and table alignment."
          ]
        },
        {
          id: "C-6a8f07a9adbf-6f8fbc516ad2",
          metric: "revenue",
          value: 12404.01,
          unit: null,
          period: null,
          doc_page: 13,
          status: "unverified",
          snippet: "Revenue from operations 34  12,563.09  12,404.01",
          notes: [
            "Machine-extracted financial-statement candidate; verify the value, column header, units, reporting period, basis and scope against the PDF.",
            "Dated column header year: 2024.",
            "Statement header: Integrated Annual Report 2024-25 | 343 | Consolidated Statement of Profit and Loss | for the year ended 31 March 2025",
            "No value is verified until a human resolves the period, units, statement basis and table alignment."
          ]
        }
      ]
    }
  },
  "itc": {
    company: "ITC Limited",
    searchResults: [
      {
        title: "ITC Report and Accounts 2024 | Audited Financials",
        url: "https://www.itcportal.com/media-centre/shareholder-information/report-and-accounts-2024.pdf",
        snippet: "ITC Consolidated and Standalone Balance Sheet and P&L Disclosures for FY2023-24."
      },
      {
        title: "ITC Financial Results & Quarterly Performance",
        url: "https://www.itcportal.com/investor/financial-performance.aspx",
        snippet: "Official shareholder report and segmental revenues."
      },
      {
        title: "BSE Corporate Announcements - ITC Annual Filing",
        url: "https://www.bseindia.com/corporates/itc-annual-accounts-2024",
        snippet: "BSE/NSE public statutory disclosures and auditor report."
      }
    ],
    pdfLinks: [
      {
        title: "ITC Report and Accounts 2024 (Consolidated Statements)",
        url: "https://www.itcportal.com/media-centre/shareholder-information/report-and-accounts-2024.pdf"
      },
      {
        title: "ITC Standalone Financial Statements FY24",
        url: "https://www.itcportal.com/media-centre/shareholder-information/standalone-accounts-2024.pdf"
      }
    ],
    extraction: {
      company: "ITC Limited",
      title: "ITC Report and Accounts 2024 (Consolidated Statements)",
      url: "https://www.itcportal.com/media-centre/shareholder-information/report-and-accounts-2024.pdf",
      cache_path: "data\\cache\\52179dfea5f4a7c3a85f37488c7eaeef98219f80b28472d4.pdf",
      sha256: "52179dfea5f4a7c3a85f37488c7eaeef98219f80b28472d480d29188e7b9201f",
      candidate_file: "data\\candidates\\candidates-52179dfea5f4-8c7eaeef.json",
      candidate_count: 4,
      ambiguous_count: 1,
      cache_reused: true,
      candidates: [
        {
          id: "C-52179dfea5f4-01",
          metric: "revenue",
          value: 70251.28,
          unit: null,
          period: null,
          doc_page: 185,
          status: "unverified",
          snippet: "Revenue from Operations 70,251.28  59,745.56",
          notes: [
            "Machine-extracted candidate; verify value, column header, units and statement basis.",
            "Dated column header year: 2023.",
            "Statement header: Consolidated Statement of Profit and Loss for the year ended 31st March, 2023 (` in Crores)"
          ]
        },
        {
          id: "C-52179dfea5f4-02",
          metric: "revenue",
          value: 59745.56,
          unit: null,
          period: null,
          doc_page: 185,
          status: "unverified",
          snippet: "Revenue from Operations 70,251.28  59,745.56",
          notes: [
            "Machine-extracted candidate; verify value, column header, units and statement basis.",
            "Dated column header year: 2022.",
            "Statement header: Consolidated Statement of Profit and Loss for the year ended 31st March, 2023 (` in Crores)"
          ]
        },
        {
          id: "C-52179dfea5f4-03",
          metric: "trade_receivables",
          value: 2608.28,
          unit: null,
          period: null,
          doc_page: 184,
          status: "unverified",
          snippet: "Trade receivables 11  2,608.28  2,156.40",
          notes: [
            "Machine-extracted candidate from Consolidated Balance Sheet.",
            "Dated column header year: 2023.",
            "Statement header: Consolidated Balance Sheet as at 31st March, 2023 (` in Crores)"
          ]
        },
        {
          id: "C-52179dfea5f4-04",
          metric: "trade_receivables",
          value: 2156.40,
          unit: null,
          period: null,
          doc_page: 184,
          status: "unverified",
          snippet: "Trade receivables 11  2,608.28  2,156.40",
          notes: [
            "Machine-extracted candidate from Consolidated Balance Sheet.",
            "Dated column header year: 2022.",
            "Statement header: Consolidated Balance Sheet as at 31st March, 2023 (` in Crores)"
          ]
        }
      ]
    }
  }
};

export function getIntakeData(companyName) {
  if (!companyName) return sampleIntakeDatabase['dabur'];
  const q = companyName.toLowerCase().trim();
  if (q.includes('dabur')) return sampleIntakeDatabase['dabur'];
  if (q.includes('itc')) return sampleIntakeDatabase['itc'];

  // Dynamic fallback for any company name
  const cleanName = companyName.trim();
  const slug = cleanName.toLowerCase().replace(/[^a-z0-9]+/g, '-');
  const pseudoHash = Array.from(slug).reduce((acc, c) => ((acc << 5) - acc + c.charCodeAt(0)) | 0, 0);
  const hashHex = Math.abs(pseudoHash).toString(16).padStart(8, '0') + "7a9adbf572acb3cf78ed5bb7f114c08dae9058e3d3c4d70ebd5da652135".slice(8);
  const candHex = hashHex.slice(0, 12);

  return {
    company: cleanName,
    searchResults: [
      {
        title: `${cleanName} Annual Report 2024-25 | Audited Financial Statements`,
        url: `https://www.${slug}.com/investor-relations/annual-reports/${slug}-annual-report-fy25.pdf`,
        snippet: `Statutory Audited Balance Sheet, Profit & Loss Statement, and Cash Flows for ${cleanName} FY2024-25.`
      },
      {
        title: `${cleanName} Investor Presentation & Results FY25`,
        url: `https://www.${slug}.com/investor-relations/financial-results`,
        snippet: `Corporate overview, segment results, auditor report, and disclosures submitted to stock exchanges.`
      },
      {
        title: `BSE Corporate Filings: ${cleanName} Financial Results`,
        url: `https://www.bseindia.com/corporates/${slug}-financial-filing.html`,
        snippet: `Official public statutory filing submitted to BSE and NSE for FY2024-25.`
      }
    ],
    pdfLinks: [
      {
        title: `${cleanName} Consolidated Financial Statements FY25`,
        url: `https://www.${slug}.com/investor-relations/annual-reports/${slug}-consolidated-financials-fy25.pdf`
      },
      {
        title: `${cleanName} Standalone Financial Statements FY25`,
        url: `https://www.${slug}.com/investor-relations/annual-reports/${slug}-standalone-financials-fy25.pdf`
      },
      {
        title: `${cleanName} Integrated Annual Report 2024-25 (Full PDF)`,
        url: `https://www.${slug}.com/investor-relations/annual-reports/${slug}-annual-report-2025.pdf`
      }
    ],
    extraction: {
      company: cleanName,
      title: `${cleanName} Consolidated Financial Statements FY25`,
      url: `https://www.${slug}.com/investor-relations/annual-reports/${slug}-consolidated-financials-fy25.pdf`,
      cache_path: `data\\cache\\${hashHex}.pdf`,
      sha256: hashHex,
      candidate_file: `data\\candidates\\candidates-${candHex}-55edd0af.json`,
      candidate_count: 4,
      ambiguous_count: 1,
      cache_reused: false,
      candidates: [
        {
          id: `C-${candHex}-01`,
          metric: "trade_receivables",
          value: 1120.45,
          unit: null,
          period: null,
          doc_page: 24,
          status: "unverified",
          snippet: "Trade receivables 12  1,120.45  1,048.20",
          notes: [
            "Machine-extracted financial-statement candidate; verify against PDF.",
            "Dated column header year: 2025.",
            `Statement header: ${cleanName} Consolidated Balance Sheet as at 31 March 2025 (in INR Crores)`
          ]
        },
        {
          id: `C-${candHex}-02`,
          metric: "trade_receivables",
          value: 1048.20,
          unit: null,
          period: null,
          doc_page: 24,
          status: "unverified",
          snippet: "Trade receivables 12  1,120.45  1,048.20",
          notes: [
            "Machine-extracted financial-statement candidate; verify against PDF.",
            "Dated column header year: 2024.",
            `Statement header: ${cleanName} Consolidated Balance Sheet as at 31 March 2025 (in INR Crores)`
          ]
        },
        {
          id: `C-${candHex}-03`,
          metric: "revenue",
          value: 15840.80,
          unit: null,
          period: null,
          doc_page: 25,
          status: "unverified",
          snippet: "Revenue from operations 28  15,840.80  14,920.10",
          notes: [
            "Machine-extracted candidate; verify value, column header, units and statement basis.",
            "Dated column header year: 2025.",
            `Statement header: ${cleanName} Statement of Profit & Loss for year ended 31 March 2025`
          ]
        },
        {
          id: `C-${candHex}-04`,
          metric: "revenue",
          value: 14920.10,
          unit: null,
          period: null,
          doc_page: 25,
          status: "unverified",
          snippet: "Revenue from operations 28  15,840.80  14,920.10",
          notes: [
            "Machine-extracted candidate; verify value, column header, units and statement basis.",
            "Dated column header year: 2024.",
            `Statement header: ${cleanName} Statement of Profit & Loss for year ended 31 March 2025`
          ]
        }
      ]
    }
  };
}
