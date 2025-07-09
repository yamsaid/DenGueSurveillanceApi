/**
 * Page Indicateurs - JavaScript
 * Système de surveillance de la dengue
 */

// ===== CONFIGURATION GLOBALE =====
const CONFIG = {
    // Configuration PowerBI (mode public - essai gratuit)
    powerBI: {
        // URL publique du rapport PowerBI (obtenue depuis PowerBI Service)
        publicUrl: 'https://app.powerbi.com/view?r=eyJrIjoiN2QyMzZmYWYtNTllOS00MTNlLWI0NzYtYzNhZTRiNDRmYjIyIiwidCI6IjdmYzlhNjBkLTViMDAtNDdmOS04NDRhLTg2YWI1YzNhNTVmMyJ9&embedImagePlaceholder=true',
        // Hauteur de l'iframe (en pixels)
        height: 600,
        // Largeur de l'iframe (en pourcentage)
        width: 1490
    },
    
    // API Endpoints
    api: {
        stats: '/api/stats',
        regions: '/api/regions',
        districts: '/api/districts',
        hebdomadaires: '/api/data/hebdomadaires',
        mensuels: '/api/data/mensuels'
    },
    
    // Paramètres par défaut
    defaults: {
        dateRange: 30,
        region: 'Toutes',
        district: 'Toutes',
        serotype: 'Tous'
    }
};

// ===== CLASSE DASHBOARD STATE =====
class DashboardState {
    constructor() {
        this.filters = {
            dateRange: CONFIG.defaults.dateRange,
            region: CONFIG.defaults.region,
            district: CONFIG.defaults.district,
            serotype: CONFIG.defaults.serotype,
            startDate: null,
            endDate: null
        };
        this.powerBIReport = null;
        this.isLoading = false;
        this.isDarkMode = localStorage.getItem('darkMode') === 'true';
        this.regions = [];
        this.districts = [];
    }
    
    // Mise à jour des filtres
    updateFilters(newFilters) {
        this.filters = { ...this.filters, ...newFilters };
        this.saveFilters();
        this.applyFilters();
    }
    
    // Application des filtres
    async applyFilters() {
        if (this.powerBIReport) {
            try {
                await this.powerBIReport.setFilters(this.filters);
                this.updateQuickStats();
            } catch (error) {
                console.error('Erreur lors de l\'application des filtres:', error);
                showError('Erreur lors de l\'application des filtres');
            }
        }
    }
    
    // Sauvegarde des filtres
    saveFilters() {
        localStorage.setItem('dashboardFilters', JSON.stringify(this.filters));
    }
    
    // Chargement des filtres sauvegardés
    loadFilters() {
        const saved = localStorage.getItem('dashboardFilters');
        if (saved) {
            this.filters = { ...this.filters, ...JSON.parse(saved) };
        }
    }
    
    // Basculement du mode sombre
    toggleDarkMode() {
        this.isDarkMode = !this.isDarkMode;
        document.documentElement.setAttribute('data-theme', this.isDarkMode ? 'dark' : 'light');
        localStorage.setItem('darkMode', this.isDarkMode);
        
        const icon = document.querySelector('#dark-mode-btn i');
        icon.className = this.isDarkMode ? 'fas fa-sun' : 'fas fa-moon';
    }
}

// ===== INSTANCE GLOBALE =====
const dashboardState = new DashboardState();

// ===== INITIALISATION =====
document.addEventListener('DOMContentLoaded', async function() {
    try {
        // Initialisation
        initializeApp();
        
        // Chargement des données
        await loadInitialData();
        
        // Configuration des événements
        setupEventListeners();
        
        // Chargement du rapport PowerBI
        await embedPowerBIReport();
        
        // Masquage du loading
        hideLoadingOverlay();
        
    } catch (error) {
        console.error('Erreur lors de l\'initialisation:', error);
        showError('Erreur lors de l\'initialisation de l\'application');
        hideLoadingOverlay();
    }
});

// ===== FONCTIONS D'INITIALISATION =====
function initializeApp() {
    // Application du mode sombre si activé
    if (dashboardState.isDarkMode) {
        document.documentElement.setAttribute('data-theme', 'dark');
        const icon = document.querySelector('#dark-mode-btn i');
        icon.className = 'fas fa-sun';
    }
    
    // Chargement des filtres sauvegardés
    dashboardState.loadFilters();
    
    // Application des filtres aux contrôles
    applyFiltersToControls();
}

async function loadInitialData() {
    // Chargement des régions
    await loadRegions();
    
    // Chargement des districts
    await loadDistricts();
    
    // Chargement des statistiques rapides
    await updateQuickStats();
}

function setupEventListeners() {
    // Filtres
    document.getElementById('apply-filters').addEventListener('click', applyFilters);
    document.getElementById('reset-filters').addEventListener('click', resetFilters);
    document.getElementById('save-filters').addEventListener('click', saveFilters);
    
    // Sélecteurs de filtres
    document.getElementById('date-range').addEventListener('change', onDateRangeChange);
    document.getElementById('region-filter').addEventListener('change', onRegionChange);
    document.getElementById('district-filter').addEventListener('change', onDistrictChange);
    document.getElementById('serotype-filter').addEventListener('change', onSerotypeChange);
    
    // Actions header
    document.getElementById('refresh-btn').addEventListener('click', refreshData);
    document.getElementById('export-pdf-btn').addEventListener('click', () => exportReport('pdf'));
    document.getElementById('export-excel-btn').addEventListener('click', () => exportReport('excel'));
    document.getElementById('share-btn').addEventListener('click', showShareModal);
    document.getElementById('dark-mode-btn').addEventListener('click', () => dashboardState.toggleDarkMode());
    
    // Actions PowerBI
    document.getElementById('fullscreen-btn').addEventListener('click', toggleFullscreen);
    document.getElementById('refresh-report-btn').addEventListener('click', refreshPowerBIReport);
    
    // Actions section
    document.getElementById('export-full-report').addEventListener('click', exportFullReport);
    document.getElementById('print-report').addEventListener('click', printReport);
    
    // Modal
    document.getElementById('copy-url').addEventListener('click', copyShareUrl);
    
    // Raccourcis clavier
    document.addEventListener('keydown', handleKeyboardShortcuts);
}

// ===== GESTION DES FILTRES =====
function applyFiltersToControls() {
    const { dateRange, region, district, serotype } = dashboardState.filters;
    
    document.getElementById('date-range').value = dateRange;
    document.getElementById('region-filter').value = region;
    document.getElementById('district-filter').value = district;
    document.getElementById('serotype-filter').value = serotype;
}

async function applyFilters() {
    try {
        showLoadingState();
        
        const newFilters = {
            dateRange: parseInt(document.getElementById('date-range').value),
            region: document.getElementById('region-filter').value,
            district: document.getElementById('district-filter').value,
            serotype: document.getElementById('serotype-filter').value
        };
        
        // Calcul des dates
        const { startDate, endDate } = calculateDateRange(newFilters.dateRange);
        newFilters.startDate = startDate;
        newFilters.endDate = endDate;
        
        dashboardState.updateFilters(newFilters);
        
        // Mise à jour des statistiques
        await updateQuickStats();
        
        showSuccess('Filtres appliqués avec succès');
        
    } catch (error) {
        console.error('Erreur lors de l\'application des filtres:', error);
        showError('Erreur lors de l\'application des filtres');
    } finally {
        hideLoadingState();
    }
}

function resetFilters() {
    dashboardState.filters = {
        dateRange: CONFIG.defaults.dateRange,
        region: CONFIG.defaults.region,
        district: CONFIG.defaults.district,
        serotype: CONFIG.defaults.serotype,
        startDate: null,
        endDate: null
    };
    
    applyFiltersToControls();
    applyFilters();
}

function saveFilters() {
    dashboardState.saveFilters();
    showSuccess('Filtres sauvegardés');
}

// ===== GESTION DES ÉVÉNEMENTS DE FILTRES =====
function onDateRangeChange() {
    const dateRange = document.getElementById('date-range').value;
    if (dateRange === 'custom') {
        showCustomDatePicker();
    }
}

async function onRegionChange() {
    const region = document.getElementById('region-filter').value;
    await loadDistricts(region);
    document.getElementById('district-filter').value = 'Toutes';
}

function onDistrictChange() {
    // Logique spécifique si nécessaire
}

function onSerotypeChange() {
    // Logique spécifique si nécessaire
}

// ===== CHARGEMENT DES DONNÉES =====
async function loadRegions() {
    try {
        const response = await fetch(CONFIG.api.regions);
        if (!response.ok) throw new Error('Erreur lors du chargement des régions');
        
        const regions = await response.json();
        dashboardState.regions = regions;
        
        const select = document.getElementById('region-filter');
        select.innerHTML = '<option value="Toutes">Toutes les régions</option>';
        
        regions.forEach(region => {
            const option = document.createElement('option');
            option.value = region;
            option.textContent = region;
            select.appendChild(option);
        });
        
    } catch (error) {
        console.error('Erreur lors du chargement des régions:', error);
    }
}

async function loadDistricts(region = null) {
    try {
        const url = region && region !== 'Toutes' 
            ? `${CONFIG.api.districts}?region=${encodeURIComponent(region)}`
            : CONFIG.api.districts;
            
        const response = await fetch(url);
        if (!response.ok) throw new Error('Erreur lors du chargement des districts');
        
        const districts = await response.json();
        dashboardState.districts = districts;
        
        const select = document.getElementById('district-filter');
        select.innerHTML = '<option value="Toutes">Tous les districts</option>';
        
        districts.forEach(district => {
            const option = document.createElement('option');
            option.value = district;
            option.textContent = district;
            select.appendChild(option);
        });
        
    } catch (error) {
        console.error('Erreur lors du chargement des districts:', error);
    }
}

async function updateQuickStats() {
    try {
        const { startDate, endDate, region, district } = dashboardState.filters;
        
        const url = new URL(CONFIG.api.stats, window.location.origin);
        url.searchParams.set('date_debut', startDate);
        url.searchParams.set('date_fin', endDate);
        url.searchParams.set('region', region);
        url.searchParams.set('district', district);
        
        const response = await fetch(url);
        if (!response.ok) throw new Error('Erreur lors du chargement des statistiques');
        
        const data = await response.json();
        
        // Mise à jour des métriques
        updateMetric('total-cases', data.semaine_en_cours?.total_cases || 0);
        updateMetric('positive-cases', data.semaine_en_cours?.total_positives || 0);
        updateMetric('hospitalizations', data.semaine_en_cours?.total_hospitalized || 0);
        updateMetric('deaths', data.semaine_en_cours?.total_deaths || 0);
        
        // Mise à jour des tendances avec les données dynamiques de l'API
        updateTrendFromAPI('cases-trend', data.semaine_en_cours?.growth_cases || 0);
        updateTrendFromAPI('positive-trend', data.semaine_en_cours?.growth_positives || 0);
        updateTrendFromAPI('hospitalization-trend', data.semaine_en_cours?.growth_hospitalized || 0);
        updateTrendFromAPI('deaths-trend', data.semaine_en_cours?.growth_deaths || 0);
        
    } catch (error) {
        console.error('Erreur lors de la mise à jour des statistiques:', error);
        showError('Erreur lors du chargement des statistiques');
    }
}

// ===== POWERBI INTEGRATION (MODE PUBLIC) =====
async function embedPowerBIReport() {
    try {
        showPowerBILoading();
        
        const container = document.getElementById('powerbi-container');
        if (!container) {
            throw new Error('Conteneur PowerBI non trouvé');
        }
        
        // Créer l'iframe avec l'URL publique
        const iframe = document.createElement('iframe');
        iframe.src = CONFIG.powerBI.publicUrl;
        iframe.width = CONFIG.powerBI.width;
        iframe.height = CONFIG.powerBI.height;
        iframe.frameBorder = '0';
        iframe.allowFullscreen = true;
        iframe.style.border = 'none';
        iframe.style.borderRadius = '10px';
        iframe.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
        iframe.style.backgroundColor = 'white';
        
        // Événements de chargement
        iframe.onload = () => {
            hidePowerBILoading();
            dashboardState.powerBIReport = iframe;
            showSuccess('Rapport PowerBI chargé avec succès');
            console.log('Rapport PowerBI chargé en mode public');
        };
        
        iframe.onerror = () => {
            hidePowerBILoading();
            showPowerBIError('Erreur lors du chargement du rapport PowerBI');
            console.error('Erreur lors du chargement PowerBI');
        };
        
        // Vider le conteneur et ajouter l'iframe
        container.innerHTML = '';
        container.appendChild(iframe);
        
        return iframe;
        
    } catch (error) {
        console.error('Erreur lors de l\'embed PowerBI:', error);
        showPowerBIError('Erreur lors de l\'intégration PowerBI');
        throw error;
    }
}

// ===== FONCTIONS UTILITAIRES =====
function calculateDateRange(days) {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(endDate.getDate() - days);
    
    return {
        startDate: startDate.toISOString().split('T')[0],
        endDate: endDate.toISOString().split('T')[0]
    };
}

function updateMetric(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = value.toLocaleString('fr-FR');
    }
}

// Mise à jour de la tendance avec les données de l'API
function updateTrendFromAPI(elementId, growthPercentage) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const valueElement = element.querySelector('.trend-value');
    const iconElement = element.querySelector('i');
    
    if (!valueElement || !iconElement) return;
    
    let changeText = '';
    let changeIcon = 'fa-minus';
    let changeClass = 'text-secondary';
    
    // Détermination du type de changement basé sur le pourcentage de croissance
    if (growthPercentage > 0) {
        changeClass = 'text-success';
        changeIcon = 'fa-arrow-up';
        changeText = `+${growthPercentage.toFixed(1)}%`;
    } else if (growthPercentage < 0) {
        changeClass = 'text-danger';
        changeIcon = 'fa-arrow-down';
        changeText = `${growthPercentage.toFixed(1)}%`;
    } else {
        changeClass = 'text-secondary';
        changeIcon = 'fa-minus';
        changeText = '0%';
    }
    
    // Mise à jour du texte et de l'icône
    valueElement.textContent = changeText;
    iconElement.className = `fas ${changeIcon} ${changeClass}`;
}

// Fonction originale pour référence
function updateTrend(elementId, percentage) {
    const element = document.getElementById(elementId);
    if (element) {
        const valueElement = element.querySelector('.trend-value');
        const iconElement = element.querySelector('i');
        
        valueElement.textContent = `${Math.abs(percentage).toFixed(1)}%`;
        
        if (percentage > 0) {
            iconElement.className = 'fas fa-arrow-up text-success';
        } else if (percentage < 0) {
            iconElement.className = 'fas fa-arrow-down text-danger';
        } else {
            iconElement.className = 'fas fa-minus text-secondary';
        }
    }
}

// ===== GESTION DES ÉTATS =====
function showLoadingState() {
    dashboardState.isLoading = true;
    document.getElementById('loading-overlay').style.display = 'flex';
}

function hideLoadingState() {
    dashboardState.isLoading = false;
    document.getElementById('loading-overlay').style.display = 'none';
}

function showLoadingOverlay() {
    document.getElementById('loading-overlay').style.display = 'flex';
}

function hideLoadingOverlay() {
    document.getElementById('loading-overlay').style.display = 'none';
}

function showPowerBILoading() {
    document.getElementById('powerbi-loading').style.display = 'flex';
    document.getElementById('powerbi-error').style.display = 'none';
}

function hidePowerBILoading() {
    document.getElementById('powerbi-loading').style.display = 'none';
}

function showPowerBIError(message) {
    document.getElementById('powerbi-loading').style.display = 'none';
    document.getElementById('powerbi-error').style.display = 'flex';
    document.getElementById('error-message').textContent = message;
}

// ===== ACTIONS ET EXPORT =====
async function exportReport(format) {
    try {
        if (!dashboardState.powerBIReport) {
            showError('Aucun rapport PowerBI disponible');
            return;
        }
        
        showLoadingState();
        
        // En mode public, on ne peut pas exporter directement via l'API
        // On propose d'ouvrir le rapport dans un nouvel onglet pour l'export
        const container = document.getElementById('powerbi-container');
        if (container && container.querySelector('iframe')) {
            const iframe = container.querySelector('iframe');
            const reportUrl = iframe.src;
            
            // Ouvrir le rapport dans un nouvel onglet pour l'export
            window.open(reportUrl, '_blank');
            showSuccess(`Rapport ouvert dans un nouvel onglet pour l'export en ${format.toUpperCase()}`);
        } else {
            showError('Rapport PowerBI non disponible');
        }
        
    } catch (error) {
        console.error('Erreur lors de l\'export:', error);
        showError(`Erreur lors de l'export en ${format.toUpperCase()}`);
    } finally {
        hideLoadingState();
    }
}

function downloadFile(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

async function refreshData() {
    try {
        showLoadingState();
        
        // Actualiser les statistiques
        await updateQuickStats();
        
        // Actualiser le rapport PowerBI si disponible
        if (dashboardState.powerBIReport) {
            refreshPowerBIReport();
        }
        
        showSuccess('Données actualisées avec succès');
        
    } catch (error) {
        console.error('Erreur lors de l\'actualisation:', error);
        showError('Erreur lors de l\'actualisation des données');
    } finally {
        hideLoadingState();
    }
}

function refreshPowerBIReport() {
    if (dashboardState.powerBIReport) {
        // Recharger l'iframe en mode public
        const container = document.getElementById('powerbi-container');
        if (container && container.querySelector('iframe')) {
            const iframe = container.querySelector('iframe');
            iframe.src = iframe.src; // Recharger l'iframe
            showSuccess('Rapport PowerBI actualisé');
        }
    }
}

function toggleFullscreen() {
    const container = document.getElementById('powerbi-container');
    if (!document.fullscreenElement) {
        container.requestFullscreen();
    } else {
        document.exitFullscreen();
    }
}

function exportFullReport() {
    exportReport('pdf');
}

function printReport() {
    window.print();
}

// ===== PARTAGE =====
function showShareModal() {
    const modal = new bootstrap.Modal(document.getElementById('shareModal'));
    const shareUrl = generateShareUrl();
    document.getElementById('share-url').value = shareUrl;
    modal.show();
}

function generateShareUrl() {
    const url = new URL(window.location.href);
    url.searchParams.set('filters', JSON.stringify(dashboardState.filters));
    return url.toString();
}

function copyShareUrl() {
    const urlInput = document.getElementById('share-url');
    urlInput.select();
    document.execCommand('copy');
    showSuccess('Lien copié dans le presse-papiers');
}

function shareViaEmail() {
    const subject = encodeURIComponent('Rapport Indicateurs Dengue');
    const body = encodeURIComponent(`Consultez le rapport des indicateurs de surveillance de la dengue : ${generateShareUrl()}`);
    window.open(`mailto:?subject=${subject}&body=${body}`);
}

function shareViaWhatsApp() {
    const text = encodeURIComponent(`Rapport Indicateurs Dengue : ${generateShareUrl()}`);
    window.open(`https://wa.me/?text=${text}`);
}

// ===== RACCOURCIS CLAVIER =====
function handleKeyboardShortcuts(event) {
    // Ctrl/Cmd + R : Actualiser
    if ((event.ctrlKey || event.metaKey) && event.key === 'r') {
        event.preventDefault();
        refreshData();
    }
    
    // Ctrl/Cmd + E : Export PDF
    if ((event.ctrlKey || event.metaKey) && event.key === 'e') {
        event.preventDefault();
        exportReport('pdf');
    }
    
    // Ctrl/Cmd + S : Sauvegarder les filtres
    if ((event.ctrlKey || event.metaKey) && event.key === 's') {
        event.preventDefault();
        saveFilters();
    }
    
    // F11 : Plein écran
    if (event.key === 'F11') {
        event.preventDefault();
        toggleFullscreen();
    }
}

// ===== NOTIFICATIONS =====
function showSuccess(message) {
    const toast = new bootstrap.Toast(document.getElementById('successToast'));
    document.getElementById('successToastBody').textContent = message;
    toast.show();
}

function showError(message) {
    const toast = new bootstrap.Toast(document.getElementById('errorToast'));
    document.getElementById('errorToastBody').textContent = message;
    toast.show();
}

// ===== FONCTIONS DE RETRY =====
function retryLoad() {
    hidePowerBILoading();
    embedPowerBIReport();
}

// ===== GESTION DES ERREURS GLOBALES =====
window.addEventListener('error', function(event) {
    console.error('Erreur globale:', event.error);
    showError('Une erreur inattendue s\'est produite');
});

window.addEventListener('unhandledrejection', function(event) {
    console.error('Promesse rejetée:', event.reason);
    showError('Une erreur de communication s\'est produite');
});

// ===== EXPORT DES FONCTIONS GLOBALES =====
window.dashboardState = dashboardState;
window.retryLoad = retryLoad;
window.shareViaEmail = shareViaEmail;
window.shareViaWhatsApp = shareViaWhatsApp; 