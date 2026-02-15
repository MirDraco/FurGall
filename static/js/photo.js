const accordionHeaders = document.querySelectorAll(".accordion-header");

accordionHeaders.forEach((header) => {
  header.addEventListener("click", () => {
    const content = header.nextElementSibling;
    const isActive = header.classList.contains("active");

    accordionHeaders.forEach((otherHeader) => {
      if (otherHeader !== header) {
        otherHeader.classList.remove("active");
        otherHeader.nextElementSibling.classList.remove("active");
      }
    });

    header.classList.toggle("active");
    content.classList.toggle("active");
  });
});
