from langchain_community.tools import ArxivQueryRun,WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper,ArxivAPIWrapper
api_wrapper_arxiv=ArxivAPIWrapper(top_k_results=2,doc_content_chars_max=500)
arxiv=ArxivQueryRun(api_wrapper=api_wrapper_arxiv)
print(arxiv.name)
arxiv.invoke("Attention is all you need")


SSLError: HTTPSConnectionPool(host='export.arxiv.org', port=443): Max retries exceeded with url: /api/query?search_query=Attention+is+
all+you+need&id_list=&sortBy=relevance&sortOrder=descending&start=0&max_results=100 
(Caused by SSLError(SSLCertVerificationError
                    (1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1006)')))
