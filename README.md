Sistema de Gerenciamento para Clínica Veterinária Pet
📝 Descrição:
Sistema desktop desenvolvido em Python com Tkinter para gestão completa de clínica veterinária, substituindo controle manual em cadernos por solução digital prática e acessível.
✅ FUNCIONALIDADES IMPLEMENTADAS:
👥 Módulo de Clientes
✅ Cadastro completo com CEP automático (integração com API ViaCEP dos Correios — preenche endereço, bairro, cidade e estado sozinho)
✅ Botões: ➕ NOVO | ✏️ EDITAR | 🗑️ EXCLUIR com confirmação de segurança
✅ Validação e preenchimento automático de endereço
🐾 Ficha Completa do Pet
✅ Dados: Nome, Data de Nascimento, Idade calculada automaticamente, Raça, Cor, Pelagem
✅ Histórico de Vacinas (campo de texto ampliado)
✅ Controle de Última Consulta e Data de Retorno Agendado
✅ Botões: ➕ NOVO | ✏️ EDITAR | 🗑️ EXCLUIR
✅ Chave Estrangeira (FK tutor_id): só permite cadastrar Pet se o Cliente (Tutor) já estiver cadastrado — regra de integridade de banco de dados aplicada
📦 Controle de Estoque
✅ Cadastro de produtos: Nome, Quantidade, Preço de Venda
✅ Alerta visual em vermelho quando estoque está baixo (≤ 3 unidades)
✅ Botões: ➕ NOVO | ✏️ EDITAR | 🗑️ EXCLUIR
📋 Atendimentos e Serviços
✅ Registro de atendimentos: Pet, Serviço prestado, Valor, Forma de Pagamento
✅ Ligação automática com o Tutor através do Pet
✅ Botões: ➕ NOVO | ✏️ EDITAR | 🗑️ EXCLUIR
✅ Chave Estrangeira (FK pet_id): só permite registrar atendimento se o Pet existir
📊 Painel Principal / Dashboard
✅ Contadores em tempo real: Total de Clientes, Pets, Atendimentos
✅ Faturamento total calculado automaticamente
✅ Exclusão Cascate: ao excluir um Cliente, todos os Pets e Atendimentos vinculados são removidos automaticamente
💾 Armazenamento
✅ Dados salvos em arquivos JSON estruturados como tabelas
✅ Sem necessidade de instalar banco de dados separado
✅ Estrutura preparada para futura migração para SQL/NoSQL
🛠️ TECNOLOGIAS UTILIZADAS:
Python 3 + Tkinter (Interface Gráfica)
JSON (Armazenamento estruturado)
API ViaCEP (Consulta automática de endereço)
Git / GitHub (Controle de versão e salvamento na nuvem)
🎓 CONCEITOS DE BANCO DE DADOS APLICADOS:
✅ Chaves Estrangeiras → mantém vínculo e integridade entre tabelas
✅ Exclusão Cascate → remove registros vinculados
✅ Integridade Referencial → não permite dados órfãos ou inválidos
✅ Relacionamento 1:N → 1 Cliente pode ter vários Pets
🚀 COMO EXECUTAR:
bash
# Instale a biblioteca de consulta CEP (1 vez só)
pip install requests

# Execute o sistema
python sistema_clinica_pet.py
📌 RESUMO CURTO (para colocar na caixinha de "Description" do GitHub):
Sistema desktop em Python para gestão de clínica veterinária: cadastro de Clientes com CEP automático, Ficha Completa do Pet (Raça, Cor, Pelagem, Vacinas, Idade, Última Consulta e Retorno), Controle de Estoque, Atendimentos e Chaves Estrangeiras validadas. Dados salvos em JSON.
📋 COMO COLOCAR NO GITHUB:
Vá na página do seu repositório → https://github.com/mmagnoffsp/sistema_clinica_pet.py
Clique em "Edit" (lápis) ao lado do nome
No campo Description cole o Resumo Curto acima
No campo Edit README cole a Descrição Completa
Role a página e clique em Commit changes
