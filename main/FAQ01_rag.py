import ollama
from sentence_transformers import SentenceTransformer  # Fallback if needed, but we use Ollama
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re

# Your FAQ document (full text)
faq_doc = """
Badger Screw FAQ
Product Goal: Design a direct to MUA screw that maximized clamping force, while reducing screw channel stress (goldilocks zone). This was done by creating a radiused clamping area that distributes stress around the shaft and head, while prioritizing vertical clamping. By using the screw shaft to secure the prosthetic, we could create a smaller screw head. A smaller screw head preserves prosthetic and increases strength of prosthetic.
Purchasing:
Qty 10 - $240
Qty: 50 - $1,140 - 5% off & 10 free tokens ($132.50 value. $72.50 + $60)
Qty: 100 - $2,160 - 10% off & 10 free tokens ($312.50 value. $72.50 + $240)
Qty:  Please call for Bulk Order pricing
FAQ
Head diameter:2mm
Screw channel diameter: 2.04mm
Clamping force:~136N
Screw channel Stress: ~35 MPa
Driver:0.048”(1.22mm) hex driver
Needed because of smaller head diameter
No angle correctionat this time. Not needed in most cases because of smaller screw head
Can these be used with Ti bases or single unit restorations?
Designed intent was for direct to MUA application
Incorrect thread pattern for single unit – direct to implant restoration (single unit Ti base)
Design Libraries:
Exocad
3Shape
Screw channel milling centers:can be milled with 1mm endmill
Hyperdent
Millbox
Compatible MUA’s:
3i®
Adin®
Astra®
BlueSkyBio®
Biohorizons®
Cortex®
Dentsply®
Dess®
GenTek ZFX®
Hiossen®
Keystone®
Megagen®
Medentika IPS®
Neodent®
NobelBiocare®
Noris®
Osstem®
Southern Implants®
SRL®
Straumann®
Thommen Medical®
ZFX®
ZimVie®
WIB Software FAQ
Product Goal:Create a design tool that gives confidence to full arch designers that the arch is structurally sound before beginning the manufacturing process. Finite Element Analysis (FEA) is used in all engineering and manufacturing fields, we are bringing that capability to dentistry.This allows designers to understand how their design choices affect the strength of their arch.
Offers easy to understand, color coded results to quickly identify weak areas. Users will be able to view their results in a360 degree 3D viewer.
Finite Element Analysis (FEA):A computerized method for predicting how an object reacts to real-world forces. This is done by slicing the object into small triangles (or nodes) and applying theforce to that area.
Software Requirements:
Browser based token usage.
 Purchase tokens through our website.
Mobile Device viewing
Can viewthe results of simulations
Token Requirement:
10 tokens per patient case
6x simulations per patient case
$7.25 token –entry price
Upload Requirements:
Double Arch
Designed prosthetics aligned in occlusion
Construction info exported from design software
Single Arch
Designed single prosthetic
Opposing jaw scan aligned in occlusion
Construction info exported from design software
FAQs
Supported screw channelgeometries?
Badger
Powerball
Dess long (1.4mm thread)
Dess short
Rosen
Ti bar cases?
Not availableat this time. Monolithic cases
FDA certification?
No
What if my arch breaks anyway?
We cannot guaranteearch designs due to errors in manufacturing, implant position, and instillation of the arch.
Where do stress points commonly occur?
See for yourself with 6x simulations per patient case. Stress areas show up on cantilevers, between teeth, on MUA bases, and sharp transitions between geometries
Where do I access the simulations?
WIB portal button on our website
Patient information? HIPAA
Patient information is encrypted and scrambled upon entry
Smart Mouth FAQ
Who we are:
Combining the knowledge of dental professionals and engineers to create innovative products.
We wanted to solve pain points in full arch restorations, such as premature prosthetic breakage, long chair time, and inaccurate post op digital conversions.
Created 2023. Launching 2025
Launching 5-6 new products in 2025 including new hardware and software.
"""

# Chunk the document
def chunk_doc(text, chunk_size=200):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""
    for sent in sentences:
        if len(current_chunk.split()) + len(sent.split()) < chunk_size:
            current_chunk += sent + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sent + " "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

chunks = chunk_doc(faq_doc)

# Embed with Ollama
def embed_text(text):
    response = ollama.embeddings(model='snowflake-arctic-embed', prompt=text)
    return np.array(response['embedding'])

# Embed all chunks
print("Embedding chunks...")
chunk_embeddings = [embed_text(chunk) for chunk in chunks]
print(f"Embedded {len(chunks)} chunks")

# Retrieve relevant chunks
def retrieve_chunks(query, top_k=3):
    query_emb = embed_text(query)
    similarities = cosine_similarity([query_emb], chunk_embeddings)[0]
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    return [chunks[i] for i in top_indices]

# Generate answer with Ollama
def generate_answer(query, context):
    prompt = f"""Context from FAQ docs:
{context}

Question: {query}

Answer concisely based on the context above:"""
    response = ollama.generate(model='llama3.2', prompt=prompt)
    return response['response'].strip()

# Main query function
def ask_rag(query):
    relevant_chunks = retrieve_chunks(query)
    context = "\n\n".join(relevant_chunks)
    answer = generate_answer(query, context)
    return answer

# Interactive loop
if __name__ == "__main__":
    print("Simple RAG AI ready! Ask about Smart Mouth products (type 'quit' to exit)")
    while True:
        query = input("\nYou: ").strip()
        if query.lower() == 'quit':
            break
        if query:
            answer = ask_rag(query)
            print(f"AI: {answer}")