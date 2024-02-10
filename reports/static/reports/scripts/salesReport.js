const reportTable = document.querySelector('#sales-report-table');
const printReportButton = document.querySelector('#print-report');

disableHeaderSearch();


function prettyPrintTable(table) {
    const printWindow = window.open('', '', 'width=800, height=600');
    printWindow.document.write('<html><head><title>Sales Report</title>');
    printWindow.document.write('</head><body>');
    printWindow.document.write(table.outerHTML);
    printWindow.document.write('</body></html>');
    printWindow.document.close();
    printWindow.print();
}

printReportButton.addEventListener('click', () => {
    prettyPrintTable(reportTable);
});
