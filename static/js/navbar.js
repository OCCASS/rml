window.onload = () => {
  const button = document.getElementById("burger");
  const navbar = document.getElementById("navbar");

  const hide = () => {
    navbar.classList.remove("show");
    document.documentElement.classList.remove("noscroll");
  };

  const show = () => {
    navbar.classList.add("show");
    document.documentElement.classList.add("noscroll");
  };

  button.addEventListener("click", () => {
    if (navbar.classList.contains("show")) {
      hide();
    } else {
      show();
    }
  });

  const navbarLinks = document.querySelectorAll("#navbar a");
  navbarLinks.forEach((link) => {
    link.addEventListener("click", () => {
      hide();
    });
  });
};
