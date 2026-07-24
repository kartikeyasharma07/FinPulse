import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'

export async function exportElementAsPdf(element, filename) {
  const canvas = await html2canvas(element, {
    backgroundColor: getComputedStyle(document.body).backgroundColor,
    scale: 2,
  })
  const imgData = canvas.toDataURL('image/png')

  const pdf = new jsPDF({
    orientation: 'portrait',
    unit: 'px',
    format: [canvas.width, canvas.height],
  })
  pdf.addImage(imgData, 'PNG', 0, 0, canvas.width, canvas.height)
  pdf.save(filename)
}
