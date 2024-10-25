// Insert sample document
db.documents.insertOne({
  case_id: 123,
  client_id: 45,
  worker_id: 7,
  document_title: "Contract.pdf",
  document_description: "Contract for legal representation.",
  file_content: "<base64_encoded_content>",
  uploaded_by: "Admin User",
  uploaded_at: ISODate("2024-10-23T12:00:00Z"),
  last_modified: ISODate("2024-10-23T13:00:00Z"),
  file_type: "application/pdf",
  document_tags: ["contract", "legal", "confidential"]
});
