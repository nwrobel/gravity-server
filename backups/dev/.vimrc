""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"                                 Formatting:                                  "
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

" Automatically indents at logical locations.
set autoindent
set smartindent

" 1 tab == 2 spaces
set shiftwidth=2
set tabstop=2

" Tab shifts a line based on the value of shiftwidth
set smarttab

" Replaces tabs with spaces for consistent spacing in any editor
set expandtab

" Shows line numbers
"set number

" Shows the cursor's current position
set ruler

" Backspace deletes indentions, line breaks, and the start of insert
set backspace=indent,eol,start

" Keep at least 4 lines above/below the cursor
set scrolloff=4

" Sets the spellcheck, toggle with F2
:map <F2> :setlocal spell! spelllang=en_us<CR>

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"                                Highlighting:                                 "
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

" Highlights the current line
set cursorline

" Highlights text after the 75th column
:match ErrorMsg '\%>80v.\+'

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"                                  Searching:                                  "
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

" Highlights search results
set hlsearch

" Incremental search
set incsearch

" Ignore case when searching
set ignorecase

" Override 'ignorecase' when intentionally searching for uppercase letters
set smartcase

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"                                    Misc:                                     "
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

" Enables text smoothing when in a fast terminal
set ttyfast

" Set the filename to the terminal's title
set title

"set terminal colors up for 256
set t_Co=256

"set the colorscheme to hybrid
colorscheme hybrid
let g:hybrid_use_Xresources = 1

" Always insert in paste mode
set paste
