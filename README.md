# Receipt-generating Website for the Casa Oceane Bed & Breakfast

This website allows a bed & breakfast called Casa Oceane in Casablanca, Morocco to easily and quickly generate receipts. While it usually took the owners around 5 minutes per receipt, they can now generate them in under 30 seconds. 

The first page is the receipts page, which allows the user to generate receipts for both clients (people who sleep in the guest rooms) and seminars (when the living room gets rented out to groups of people). Once all the necessary information is inputted, the user is redirected to the download page to download the .docx Word file containing the completed receipt. These receipts also automatically translate numbers into written-out text in French (e.g., 100 = one hundred) as that is a requirement for Moroccan receipts. 

The second page is the statistics page, which has an Overview and an All Data section. The Overview section draws on client and seminar information stored in the database to generate simple statistics for a quick overview of the current year. These statistics include revenue (split into 'revenue from clients' and 'revenue from seminars') and client sources (what percentage of clients come from AirBnB, and what percentage comes from other sources such as word of mouth). The All Data section is split into Client and Seminar, and allows the user to view all data entries in the database. It also has links that allow the user to download the entire database (split into client and seminar) as CSV files ready for processing in Excel or Google Spreadsheets. 

Lastly, I've also added some additional functionality. The website is locked with a password (no new users can register since this is specific to this bed & breakfast), the Word files generated delete automatically from the website once it is downloaded by the user, and even the generated receipts are titled according to the receipt number. 

Note that this bed & breakfast unfortunately had to close down due to COVID-19. 
