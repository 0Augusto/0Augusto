#!/usr/bin/env python3
"""
Script para atualizar automaticamente o README.md
com lista de repositórios e linguagens mais usadas
"""
import os
#import requests
from datetime import datetime

# ================= CONFIGURAÇÃO =================
# O segredo GITHUB_TOKEN é fornecido automaticamente pelo GitHub Actions.
# Para teste local, defina a variável de ambiente manualmente.
GITHUB_USERNAME = "0Augusto"  # 🔁 SUBSTITUA pelo seu username se necessário
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
API_BASE_URL = "https://api.github.com"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}
# ================================================

def get_all_repositories():
    """Obtém todos os repositórios públicos do usuário, ignorando forks."""
    repos = []
    page = 1
    while True:
        url = f"{API_BASE_URL}/users/{GITHUB_USERNAME}/repos?page={page}&per_page=100"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        if not data:
            break
        for repo in data:
            # Filtra para incluir apenas repositórios que NÃO são forks
            if not repo['fork']:
                repos.append({
                    'name': repo['name'],
                    'url': repo['html_url'],
                    'description': repo['description'] or 'Sem descrição',
                    'language': repo['language'] or 'Outro',
                    'stars': repo['stargazers_count'],
                    'updated_at': repo['updated_at']
                })
        page += 1
    # Ordena por data de atualização (mais recente primeiro)
    repos.sort(key=lambda x: x['updated_at'], reverse=True)
    return repos

def get_language_stats(repos):
    """Calcula a frequência das linguagens em todos os repositórios."""
    language_count = {}
    for repo in repos:
        lang = repo['language']
        if lang in language_count:
            language_count[lang] += 1
        else:
            language_count[lang] = 1
    # Ordena do mais para o menos usado
    sorted_languages = sorted(language_count.items(), key=lambda x: x[1], reverse=True)
    return sorted_languages

def generate_languages_section(sorted_languages):
    """Gera o markdown para a seção de linguagens (com barras de progresso)."""
    if not sorted_languages:
        return "## 📊 Linguagens Mais Usadas\n\n*Ainda não há dados de linguagem.*\n"
    
    markdown = "## 📊 Linguagens Mais Usadas\n"
    markdown += "*Ordem decrescente de uso nos meus repositórios:*\n\n"
    
    total_repos = sum(count for _, count in sorted_languages)
    
    for lang, count in sorted_languages:
        percentage = (count / total_repos) * 100
        # Cria uma barra de progresso visual (20 caracteres)
        bar_length = int(percentage / 5)
        bar = "█" * bar_length + "░" * (20 - bar_length)
        
        markdown += f"**{lang}** - {count} repo(s)\n"
        markdown += f"`{bar}` {percentage:.1f}%\n\n"
    
    return markdown

def generate_repositories_section(repos):
    """Gera uma tabela markdown com os repositórios."""
    if not repos:
        return "## 📂 Meus Repositórios\n\n*Nenhum repositório público encontrado.*\n"
    
    markdown = "## 📂 Meus Repositórios Públicos\n\n"
    markdown += "| Repositório | Descrição | Linguagem | Estrelas |\n"
    markdown += "|-------------|-----------|-----------|----------|\n"
    
    for repo in repos[:15]:  # Limita aos 15 mais recentes para não ficar muito longo
        name_link = f"[{repo['name']}]({repo['url']})"
        desc = repo['description'][:80] + "..." if len(repo['description']) > 80 else repo['description']
        lang = repo['language']
        stars = repo['stars']
        
        markdown += f"| {name_link} | {desc} | {lang} | ⭐ {stars} |\n"
    
    if len(repos) > 15:
        markdown += f"\n*Mostrando os 15 repositórios mais recentes. Total: {len(repos)}.*\n"
    
    return markdown

def update_readme(languages_section, repos_section):
    """Substitui as seções específicas no README.md."""
    try:
        with open('README.md', 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        print("❌ Erro: README.md não encontrado no diretório atual.")
        return False
    
    # Substitui a seção de linguagens (entre marcadores específicos)
    start_lang = "<!-- START_LANGUAGES -->"
    end_lang = "<!-- END_LANGUAGES -->"
    if start_lang in content and end_lang in content:
        before = content.split(start_lang)[0]
        after = content.split(end_lang)[1]
        content = before + start_lang + "\n" + languages_section + "\n" + end_lang + after
    
    # Substitui a seção de repositórios (entre marcadores específicos)
    start_repos = "<!-- START_REPOSITORIES -->"
    end_repos = "<!-- END_REPOSITORIES -->"
    if start_repos in content and end_repos in content:
        before = content.split(start_repos)[0]
        after = content.split(end_repos)[1]
        content = before + start_repos + "\n" + repos_section + "\n" + end_repos + after
    
    # Atualiza a data no rodapé
    current_date = datetime.now().strftime("%d/%m/%Y %H:%M")
    content = content.replace("{{ date }}", current_date)
    
    # Salva o arquivo atualizado
    with open('README.md', 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"✅ README.md atualizado com sucesso em {current_date}!")
    return True

def main():
    print("🚀 Iniciando a atualização do README...")
    
    try:
        # 1. Buscar repositórios
        print("📦 Buscando repositórios...")
        repos = get_all_repositories()
        print(f"   Encontrados {len(repos)} repositórios (excluindo forks).")
        
        # 2. Calcular estatísticas de linguagem
        print("💻 Calculando uso de linguagens...")
        language_stats = get_language_stats(repos)
        print(f"   {len(language_stats)} linguagens diferentes detectadas.")
        
        # 3. Gerar o conteúdo Markdown
        languages_section = generate_languages_section(language_stats)
        repos_section = generate_repositories_section(repos)
        
        # 4. Atualizar o arquivo README.md
        update_readme(languages_section, repos_section)
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão com a API do GitHub: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()
