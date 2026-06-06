STM32 TinyML GitHub Pages Website

Files included:
- index.html
- output_demo.mp4

Option A: Make this a separate GitHub Pages site
1. Create a new public GitHub repository, for example: stm32-tinyml-demo
2. Upload index.html and output_demo.mp4 to the repository root.
3. Go to Settings > Pages.
4. Under Build and deployment, select:
   Source: Deploy from a branch
   Branch: main
   Folder: /root
5. Save.
6. Your site will be available at:
   https://YOUR_USERNAME.github.io/stm32-tinyml-demo/

Option B: Add inside your existing portfolio website
1. In your existing portfolio repo, create this folder:
   projects/stm32-tinyml/
2. Upload index.html and output_demo.mp4 inside that folder.
3. Your live page will be:
   https://YOUR_USERNAME.github.io/YOUR_REPO_NAME/projects/stm32-tinyml/
4. Add a button/link in your portfolio project card:
   <a class="btn-outline" href="projects/stm32-tinyml/" target="_blank">View Interactive Demo</a>
