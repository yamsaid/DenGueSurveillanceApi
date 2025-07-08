"""
Module d'authentification pour le client Appi Dengue

Ce module gère l'authentification JWT et les opérations utilisateur.
"""

import jwt
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from .models import User, LoginRequest, RegisterRequest
from .exceptions import AuthenticationError, APIError


class AuthManager:
    """
    Gestionnaire d'authentification pour le client Appi.
    
    Cette classe gère l'authentification JWT, la gestion des tokens
    et les opérations utilisateur.
    """
    
    def __init__(self, client):
        """
        Initialise le gestionnaire d'authentification.
        
        Args:
            client: Instance du client Appi
        """
        self.client = client
        self.logger = logging.getLogger(__name__)
        self._current_user = None
        self._access_token = None
        self._token_expires_at = None
    
    def authenticate(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authentifie l'utilisateur et récupère un token JWT.
        
        Args:
            email: Adresse email
            password: Mot de passe
            
        Returns:
            Informations d'authentification
            
        Raises:
            AuthenticationError: En cas d'échec d'authentification
        """
        try:
            # Préparer les données de connexion
            login_data = {
                'email': email,
                'password': password
            }
            
            # Effectuer la requête d'authentification
            response = self.client._make_request(
                method="POST",
                endpoint="/login",
                data=login_data,
                use_form_data=True
            )
            
            # Extraire le token
            if 'access_token' in response:
                self._access_token = response['access_token']
                self._token_expires_at = datetime.now() + timedelta(minutes=30)
                
                # Mettre à jour les headers d'autorisation
                self.client.session.headers.update({
                    'Authorization': f'Bearer {self._access_token}'
                })
                
                self.logger.info(f"Authentification réussie pour {email}")
                return response
            else:
                raise AuthenticationError("Token d'accès non trouvé dans la réponse")
                
        except Exception as e:
            self.logger.error(f"Échec de l'authentification: {e}")
            raise AuthenticationError(f"Échec de l'authentification: {e}")
    
    def logout(self) -> bool:
        """
        Déconnecte l'utilisateur.
        
        Returns:
            True si la déconnexion a réussi
        """
        try:
            # Effectuer la requête de déconnexion
            self.client._make_request(
                method="POST",
                endpoint="/logout"
            )
            
            # Nettoyer les données locales
            self._current_user = None
            self._access_token = None
            self._token_expires_at = None
            
            # Retirer l'autorisation des headers
            if 'Authorization' in self.client.session.headers:
                del self.client.session.headers['Authorization']
            
            self.logger.info("Déconnexion réussie")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la déconnexion: {e}")
            return False
    
    def get_profile(self) -> User:
        """
        Récupère le profil de l'utilisateur connecté.
        
        Returns:
            Informations du profil utilisateur
            
        Raises:
            AuthenticationError: Si l'utilisateur n'est pas connecté
        """
        try:
            data = self.client._make_request("GET", "/profile")
            user = User(**data)
            self._current_user = user
            return user
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération du profil: {e}")
            raise AuthenticationError(f"Impossible de récupérer le profil: {e}")
    
    def update_profile(self, **kwargs) -> User:
        """
        Met à jour le profil utilisateur.
        
        Args:
            **kwargs: Champs à mettre à jour
            
        Returns:
            Profil utilisateur mis à jour
            
        Raises:
            AuthenticationError: Si l'utilisateur n'est pas connecté
        """
        try:
            data = self.client._make_request(
                method="PUT",
                endpoint="/profile",
                data=kwargs
            )
            
            user = User(**data)
            self._current_user = user
            return user
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour du profil: {e}")
            raise AuthenticationError(f"Impossible de mettre à jour le profil: {e}")
    
    def register(self, 
                first_name: str,
                last_name: str,
                email: str,
                username: str,
                password: str,
                terms: bool = True,
                newsletter: bool = False) -> Dict[str, Any]:
        """
        Inscrit un nouvel utilisateur.
        
        Args:
            first_name: Prénom
            last_name: Nom de famille
            email: Adresse email
            username: Nom d'utilisateur
            password: Mot de passe
            terms: Acceptation des termes
            newsletter: Inscription à la newsletter
            
        Returns:
            Résultat de l'inscription
            
        Raises:
            AuthenticationError: En cas d'échec d'inscription
        """
        try:
            register_data = {
                'firstName': first_name,
                'lastName': last_name,
                'email': email,
                'username': username,
                'password': password,
                'terms': terms,
                'newsletter': newsletter
            }
            
            response = self.client._make_request(
                method="POST",
                endpoint="/register",
                data=register_data
            )
            
            self.logger.info(f"Inscription réussie pour {email}")
            return response
            
        except Exception as e:
            self.logger.error(f"Échec de l'inscription: {e}")
            raise AuthenticationError(f"Échec de l'inscription: {e}")
    
    def change_password(self, current_password: str, new_password: str) -> bool:
        """
        Change le mot de passe de l'utilisateur.
        
        Args:
            current_password: Mot de passe actuel
            new_password: Nouveau mot de passe
            
        Returns:
            True si le changement a réussi
            
        Raises:
            AuthenticationError: En cas d'échec
        """
        try:
            data = {
                'current_password': current_password,
                'new_password': new_password
            }
            
            self.client._make_request(
                method="POST",
                endpoint="/change-password",
                data=data
            )
            
            self.logger.info("Changement de mot de passe réussi")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors du changement de mot de passe: {e}")
            raise AuthenticationError(f"Impossible de changer le mot de passe: {e}")
    
    def forgot_password(self, email: str) -> bool:
        """
        Demande une réinitialisation de mot de passe.
        
        Args:
            email: Adresse email
            
        Returns:
            True si la demande a été envoyée
            
        Raises:
            AuthenticationError: En cas d'échec
        """
        try:
            data = {'email': email}
            
            self.client._make_request(
                method="POST",
                endpoint="/forgot-password",
                data=data
            )
            
            self.logger.info(f"Demande de réinitialisation envoyée à {email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la demande de réinitialisation: {e}")
            raise AuthenticationError(f"Impossible d'envoyer la demande: {e}")
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """
        Réinitialise le mot de passe avec un token.
        
        Args:
            token: Token de réinitialisation
            new_password: Nouveau mot de passe
            
        Returns:
            True si la réinitialisation a réussi
            
        Raises:
            AuthenticationError: En cas d'échec
        """
        try:
            data = {
                'token': token,
                'new_password': new_password
            }
            
            self.client._make_request(
                method="POST",
                endpoint="/reset-password",
                data=data
            )
            
            self.logger.info("Réinitialisation de mot de passe réussie")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la réinitialisation: {e}")
            raise AuthenticationError(f"Impossible de réinitialiser le mot de passe: {e}")
    
    def is_authenticated(self) -> bool:
        """
        Vérifie si l'utilisateur est authentifié.
        
        Returns:
            True si l'utilisateur est authentifié
        """
        return self._access_token is not None and self._token_expires_at is not None
    
    def is_token_expired(self) -> bool:
        """
        Vérifie si le token JWT est expiré.
        
        Returns:
            True si le token est expiré
        """
        if self._token_expires_at is None:
            return True
        
        return datetime.now() >= self._token_expires_at
    
    def refresh_token_if_needed(self) -> bool:
        """
        Rafraîchit le token si nécessaire.
        
        Returns:
            True si le token a été rafraîchi
        """
        if self.is_token_expired():
            self.logger.warning("Token expiré, déconnexion automatique")
            self.logout()
            return False
        
        return True
    
    def get_current_user(self) -> Optional[User]:
        """
        Récupère l'utilisateur actuellement connecté.
        
        Returns:
            Utilisateur connecté ou None
        """
        if not self.is_authenticated():
            return None
        
        if self._current_user is None:
            try:
                self._current_user = self.get_profile()
            except Exception:
                return None
        
        return self._current_user
    
    def get_auth_status(self) -> Dict[str, Any]:
        """
        Récupère le statut d'authentification.
        
        Returns:
            Informations sur le statut d'authentification
        """
        try:
            return self.client._make_request("GET", "/api/auth/status")
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération du statut: {e}")
            return {
                'authenticated': False,
                'user': None,
                'error': str(e)
            } 