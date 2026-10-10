
%%
%% JOURNAL OF ENGINEERING OF CATHOLIC UNIVERSITY OF PETRÓPOLIS.
%% http://www.ucp.br
%% 
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{EngUCP}[]
%
%
\DeclareOption{10pt}{\OptionNotUsed}
\DeclareOption{11pt}{\OptionNotUsed}
\DeclareOption{twocolumn}{\OptionNotUsed}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
%
\def\EngUCPlanguage{1}
\DeclareOption{spanish}{
  \def\EngUCPlanguage{0}
}
\def\EngUCPpagenumbers{0}
\DeclareOption{pagenumbers}{
  \def\EngUCPpagenumbers{1}
}
%
\DeclareOption{english}{
  \def\EngUCPlanguage{1}
}
%
\DeclareOption{portuguese}{
  \def\EngUCPlanguage{2}
}
%
\def\EngUCPuselinks{1}
\DeclareOption{links}{
  \def\EngUCPuselinks{1}
}
\DeclareOption{nolinks}{
  \def\EngUCPuselinks{0}
}
%
\ProcessOptions\relax
%
\LoadClass[12pt]{article}
%
\RequirePackage{calc}
\RequirePackage{indentfirst}
%
% This allows that copying from PDF files preserves accents. 
\RequirePackage{times}
\RequirePackage[T1]{fontenc} % Usar T1 enconding
%
%% Title
%
\renewcommand{\@maketitle}{%
  \newpage
  \null
  \vspace{2cm}%
  {\begin{center}%
     {\fontsize{14}{16}\selectfont \bfseries \MakeUppercase{\@title} \par}%
     \vspace{12pt}%
     {
        \lineskip .5em%
        {\setlength{\tabcolsep}{0in}
        \begin{tabular}[t]{c}%
          \bfseries \@author
        \end{tabular}\par} }%
  \end{center}}% end of \parbox
  } % end of \@maketitle

%\newcommand{\abstractname}{Abstract}
\renewenvironment{abstract}{%
      \noindent \bfseries \abstractname.%
      \mdseries %\small%
}{\thispagestyle{empty}%
\pagebreak}
%
\newenvironment{keywords}
{\vspace{14pt}\noindent\textbf{\keywordsname: }}
{\vspace{12pt}}
%
\renewenvironment{thebibliography}[1]
     {\section*{\refname
        \@mkboth{\MakeUppercase\refname}{\MakeUppercase\refname}}%
      \list{\@biblabel{\@arabic\c@enumiv}}%
           {\settowidth\labelwidth{\@biblabel{#1}}%
            \leftmargin\labelwidth
            \parsep 0pt
            \itemsep 0pt
            \advance\leftmargin\labelsep
            \@openbib@code
            \usecounter{enumiv}%
            \let\p@enumiv\@empty
            \renewcommand\theenumiv{\@arabic\c@enumiv}}%
      \sloppy
      \clubpenalty4000
      \@clubpenalty \clubpenalty
      \widowpenalty4000%
      \sfcode`\.\@m}
     {\def\@noitemerr
       {\@latex@warning{Empty `thebibliography' environment}}%
      \endlist}
%
\renewcommand{\thesubsection}   {\textup{\thesection.\arabic{subsection}}}
\renewcommand{\thesubsubsection}{\textup{%
    \thesubsection .\arabic{subsubsection}}}
%
\renewcommand{\section}{\@startsection{section}{1}{0mm}%
                                     {-12pt}%
                                     {6pt}%
                                     {\bfseries\normalsize\MakeUppercase}}%
\renewcommand{\subsection}{\@startsection{subsection}{2}{0mm}%
                                     {-12pt}%
                                     {6pt}%
                                     {\bfseries\normalsize}}%

%
\setlength{\textfloatsep}{12pt}
\setlength{\abovedisplayskip}{6pt}
\setlength{\belowdisplayskip}{6pt}
\setlength{\parindent}{5mm}
\setlength{\abovecaptionskip}{6pt}
\setlength{\belowcaptionskip}{6pt}
%
\setlength{\textwidth}{16cm}
\setlength{\textheight}{24cm}
\setlength{\oddsidemargin}{-0.04cm}
\setlength{\topmargin}{8.1mm}
\setlength{\headheight}{0mm}
\setlength{\headsep}{0mm}
%
\renewcommand{\@makecaption}[2]{%
  \vspace{\abovecaptionskip}%
  {\fontsize{10}{12} \selectfont
  \sbox\@tempboxa{#1: #2}%
  \ifdim \wd\@tempboxa >\hsize
    #1: #2\par
  \else
    \global \@minipagefalse
    \hb@xt@\hsize{\hfil\box\@tempboxa\hfil}%
  \fi}
  \vskip\belowcaptionskip}
%
\def\voidaffil{$\mskip 0mu$}
%
\RequirePackage[noblocks]{authblk}
\renewcommand\AB@affilsepx{\protect\vspace{12pt}\\\protect\Affilfont }
\renewcommand\Authands{ and }
\renewcommand{\Affilfont}{\mdseries\itshape\small}
\renewcommand{\Authfont}{\bfseries}
%
\RequirePackage[numbers]{natbib}
%\bibliographystyle{plain}
%%\bibliographystyle{unsrt}
%\bibpunct{(}{)}{;}{a}{,}{,}
\setlength{\bibsep}{0pt}
%
\ifnum \EngUCPpagenumbers = 0
%\pagestyle{myheadings}
%\markboth{left head}{right head} \markright{right head}
\fi
%
%
\ifnum \EngUCPlanguage = 0
  \renewcommand\Authand{ y }%
  \renewcommand\Authands{ y }
  \RequirePackage[spanish]{babel}
  \def\keywordsname{Palabras Clave}
  \def\EngUCPbtxand{y}
  \def\EngUCPbtxeditors{editores}
  \def\EngUCPbtxeditedby{editado por}
  \def\EngUCPbtxedition{edici\'on}
  \def\EngUCPabtxvolume{volumen}
  \def\EngUCPbtxof{de}
  \def\EngUCPbtxnumber{n\'umero}
  \def\EngUCPbtxpages{p\'aginas}
  \def\EngUCPbtxchapter{cap\'\i{}tulo}
  \def\EngUCPbtxtechrep{Informe T\'ecnico}
  \def\EngUCPbtxmaster{Tesis de Maestr\'\i{}a}
  \def\EngUCPbtxphd{Tesis de Doctorado}
  \def\EngUCPbtxpage{p\'agina}
  \addto\captionsspanish{%
     \def\tablename{Tabla}}%
\fi
%
\ifnum \EngUCPlanguage = 1
  \renewcommand\Authand{ and }%
  \renewcommand\Authands{ and }
  \RequirePackage[english]{babel}
  \def\keywordsname{Keywords}
  \def\EngUCPbtxand{and}
  \def\EngUCPbtxeditors{editors}
  \def\EngUCPbtxeditedby{edited by}
  \def\EngUCPbtxedition{edition}
  \def\EngUCPbtxvolume{volume}
  \def\EngUCPbtxof{of}
  \def\EngUCPbtxnumber{number}
  \def\EngUCPbtxpages{pages}
  \def\EngUCPbtxchapter{chapter}
  \def\EngUCPbtxtechrep{Technical Report}
  \def\EngUCPbtxmaster{Master's Thesis}
  \def\EngUCPbtxphd{D.Sc. Thesis} %\def\EngUCPbtxphd{Ph.D. thesis}
  \def\EngUCPbtxpage{page}
\fi
%
\ifnum \EngUCPlanguage = 2
  \renewcommand\Authand{ e }%
  \renewcommand\Authands{ e }
  \RequirePackage[brazil]{babel}
  \def\keywordsname{Palavras Chave}
  \def\EngUCPbtxand{e}
  \def\EngUCPbtxeditors{editores}
  \def\EngUCPbtxeditors{editores}
  \def\EngUCPbtxeditedby{editado por}
  \def\EngUCPbtxedition{edi\c c\~ao}
  \def\EngUCPbtxvolume{volume}
  \def\EngUCPbtxof{de}
  \def\EngUCPbtxnumber{n\'umero}
  \def\EngUCPbtxpages{p\'aginas}
  \def\EngUCPbtxchapter{cap\'\i{}tulo}
  \def\EngUCPbtxtechrep{Relat\'orio T\'ecnico}
  \def\EngUCPbtxmaster{Disserta\c c\~ao de Mestrado}
  \def\EngUCPbtxphd{Tese de Doutorado}
  \def\EngUCPbtxpage{pagina}
\fi
%
\ifnum \EngUCPuselinks = 1

% Use color links
\RequirePackage{color}
\definecolor{url}{rgb}{0.8,0.,0.}
\RequirePackage[colorlinks,linkcolor=blue,%
                urlcolor=url,citecolor=blue,%
                plainpages=false,pdfpagelabels]{hyperref}
\RequirePackage{nameref,url}
\def\UrlFont{\mdseries}
\fi

% Theorem environments
\RequirePackage{amsthm}

\ifnum \EngUCPlanguage = 0
\theoremstyle{plain}
\newtheorem{theor}{Teorema}
\newtheorem{lemma}{Lema}
\newtheorem{corol}{Corolario}
\newtheorem{propo}{Proposici\'on}

\theoremstyle{definition}
\newtheorem{defin}{Definici\'on}
\newtheorem{examp}{Ejemplo}
\newtheorem{axiom}{Axioma}
\fi

\ifnum \EngUCPlanguage = 1
\theoremstyle{plain}
\newtheorem{theor}{Theorem}
\newtheorem{lemma}{Lemma}
\newtheorem{corol}{Corollary}
\newtheorem{propo}{Proposition}

\theoremstyle{definition}
\newtheorem{defin}{Definition}
\newtheorem{examp}{Example}
\newtheorem{axiom}{Axiom}
\fi

\ifnum \EngUCPlanguage = 2
\theoremstyle{plain}
\newtheorem{theor}{Teorema}
\newtheorem{lemma}{Lema}
\newtheorem{corol}{Corol\'ario}
\newtheorem{propo}{Proposi\c{c}\~ao}

\theoremstyle{definition}
\newtheorem{defin}{Defini\c{c}\~ao}
\newtheorem{examp}{Exemplo}
\newtheorem{axiom}{Axioma}
\fi

%%End of file
