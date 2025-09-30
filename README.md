<h2>Spend Analysis ETL Pipeline</h2>
This project was an attempt to replicate my knowledge from DE Zoomcamp by DataTalkClubs. The current pipeline extracts transactions from your downloaded statements, transforms them and loads it into a postgreDB for visulisation with any BI tools, here I will be using Metabase, which could help in analysing your expense and budget accordingly.  <br><br>


<h3>🚀 Features</h3>
- Extract
    <ul>
    <li>Parse statements from multiple cards (CSV & PDF) using pandas for csv and leveraging Amazon Bedrock for pdf's.</li>
    <li>Normalize formats into a consistent transaction structure.</li>
    <li>Store intermediate outputs as CSVs.</li>
    </ul>
- Transform
  <ul>
    <li>Clean and normalize data across cards.</li>
    <li>Categorize transactions (Groceries, Restaurants, Insurance, Loans, Gas, Entertainment)using LLM-powered categorization (Ollama).</li>
  </ul>
- Load
  <ul>
    <li>Push final transactions into PostgreSQL.</li>
    <li>Ready for visualization in tools like Metabase.</li>
  </ul>
- Orchestration
  <ul>
    <li>Managed by Airflow DAGs with task separation for Extract → Transform → Load.</li>
    <li>Uses XComs to pass file paths and metadata between tasks.</li>
  </ul>  

  ```bash
  spend_analysis/
├── airflow/               # Airflow project folder
│   ├── dags/              # DAG definitions
│   ├── config/            # (gitignored) airflow configs
│   ├── plugins/           # custom plugins if any
│   ├── logs/              # (gitignored) airflow logs
│   ├── docker-compose.yaml
│   ├── Dockerfile
│   └── .env               # environment variables (not committed)
│
├── extract/               # Data extraction layer
│   ├── bedrock_pdf_to_csv.py
│   ├── fetch_data.py
│   └── process_statements.py
│
├── transform/             # Data transformation layer
│   ├── normalise_data.py
│   └── categorise_with_ollama.py
│
├── load/                  # Database loading layer
│   └── push-data-to-db.py
│
├── statements/            # Input folder (local statements)
│
├── docker-compose.yaml    # Root-level compose file
├── Dockerfile             # Root-level Dockerfile
└── README.md


  ```

NOTE: Areas for improvement<br> 
    <ul>
        <li> Need to fix the pdf extraction logic. Using Bedrock seems to work but not very efficient and inconsistent. Eploring camelot package to find a general one-stop solution of all pdf structures </li>
        <li> Implement logic to detect and label recurring charges </li>
        <li> The logic to normalise date is hardcoded to the current year. Need to find a way to extract year from the pdf statement</li>


        
